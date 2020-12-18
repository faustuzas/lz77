from bitarray import bitarray

endian = 'big'
meta_info_element_len = 1


class LZ77Triplet:

    def __init__(self, offset, match_length, el) -> None:
        self.offset = offset
        self.match_length = match_length
        self.el = el

    def __str__(self):
        return f'({self.offset}, {self.match_length}, {self.el})'

    def __repr__(self):
        return str(self)


class ListDataIngestor:

    def __init__(self):
        self._arr = []

    def ingest(self, triplet):
        self._arr.append(triplet)

    @property
    def result(self):
        return self._arr


def list_data_loader(arr):
    arr = [a for a in arr]
    for el in arr:
        yield el


class EncodingFileTripletIngestor:

    def __init__(self, file_name, offset_size_in_bits, match_len_size_in_bits):
        self._file_name = file_name
        self._offset_size_in_bits = offset_size_in_bits
        self._match_len_size_in_bits = match_len_size_in_bits

        self._fd = None
        self._buff = bitarray()

    def __enter__(self):
        self._fd = open(self._file_name, 'wb')
        self._encode_meta_info()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush()
        self._fd.close()

    def ingest(self, triplet):
        encoded = encode_triplet(triplet, self._offset_size_in_bits, self._match_len_size_in_bits)
        self._buff.extend(encoded)

        if len(self._buff) % 8 == 0:
            self._flush()

    def _flush(self):
        self._buff.tofile(self._fd)
        self._buff.clear()

    def _encode_meta_info(self):
        offset_bytes = self._offset_size_in_bits.to_bytes(meta_info_element_len, byteorder=endian, signed=False)
        match_len_bytes = self._match_len_size_in_bits.to_bytes(meta_info_element_len, byteorder=endian, signed=False)

        self._fd.write(offset_bytes)
        self._fd.write(match_len_bytes)


class DecodingFileTripletLoader:

    def __init__(self, file_name):
        self._file_name = file_name

        # should be initialized in __enter__
        self._offset_size_in_bits = None
        self._match_len_size_in_bits = None

        self._fd = None
        self._reading_finished = False
        self._buff = bitarray()

    def __enter__(self):
        self._fd = open(self._file_name, 'rb')
        self._decode_meta_data()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fd.close()

    def __next__(self):
        triplet = self._decode_next_triplet()
        if triplet is None:
            raise StopIteration()
        return triplet

    def __iter__(self):
        return self

    @property
    def encoding_meta_data(self):
        return self._offset_size_in_bits, self._match_len_size_in_bits

    def _decode_meta_data(self):
        offset_bytes = self._fd.read(2)
        match_len_bytes = self._fd.read(2)

        self._offset_size_in_bits = int.from_bytes(offset_bytes, byteorder=endian, signed=False)
        self._match_len_size_in_bits = int.from_bytes(match_len_bytes, byteorder=endian, signed=False)

    @property
    def _triplet_len_in_bits(self):
        return self._offset_size_in_bits + self._match_len_size_in_bits + 8

    def _decode_next_triplet(self):
        if len(self._buff) < self._triplet_len_in_bits and not self._reading_finished:
            self._fill_buffer()

        return decode_triplet(self._buff, self._offset_size_in_bits, self._match_len_size_in_bits)

    def _fill_buffer(self):
        try:
            self._buff.fromfile(self._fd, 4096)
        except EOFError:
            self._reading_finished = True


class FileRawDataLoader:

    def __init__(self, file_name):
        self._file_name = file_name

        self._fd = None

    def __enter__(self):
        self._fd = open(self._file_name, 'rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fd.close()

    def __next__(self):
        byte = self._fd.read(1)
        if not byte:
            raise StopIteration()
        return byte

    def __iter__(self):
        return self


class FileRawDataIngestor:

    def __init__(self, file_name):
        self._file_name = file_name

        self._fd = None

    def __enter__(self):
        self._fd = open(self._file_name, 'wb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fd.close()

    def ingest(self, data):
        self._fd.write(data)


def encode_int_into_bits(val, size_in_bits):
    bytes_ = val.to_bytes(length=int(size_in_bits / 8) + 1, byteorder=endian, signed=False)
    bits = bitarray(endian=endian)
    bits.frombytes(bytes_)
    del bits[:8 - (size_in_bits % 8)]
    return bits


def decode_int_from_bits(bits):
    padding_size = 8 - (len(bits) % 8)
    padding = bitarray([False] * padding_size)

    padding.extend(bits)

    return int.from_bytes(padding.tobytes(), byteorder=endian, signed=False)


def encode_element(el):
    if isinstance(el, str):
        return bytes(el, encoding='ascii')
    return bytes(el)


def encode_triplet(triplet, offset_size_in_bits, match_len_size_in_bits):
    result = bitarray(endian=endian)
    result.extend(encode_int_into_bits(triplet.offset, offset_size_in_bits))
    result.extend(encode_int_into_bits(triplet.match_length, match_len_size_in_bits))
    result.frombytes(encode_element(triplet.el))
    return result


def decode_triplet(bits, offset_size_in_bits, match_len_size_in_bits):
    # only padding left
    if len(bits) < offset_size_in_bits + match_len_size_in_bits + 8:
        return None

    offset_bits = bits[:offset_size_in_bits]
    offset = decode_int_from_bits(offset_bits)

    match_len_bits = bits[offset_size_in_bits:(offset_size_in_bits + match_len_size_in_bits)]
    match_len = decode_int_from_bits(match_len_bits)

    element_bits = bits[(offset_size_in_bits + match_len_size_in_bits):(offset_size_in_bits + match_len_size_in_bits + 8)]
    element = element_bits.tobytes()

    del bits[:(offset_size_in_bits + match_len_size_in_bits + 8)]

    return LZ77Triplet(offset, match_len, element)


def search_buff_size_for_bits(bits_len):
    return (2 ** bits_len) - 1


def look_ahead_size_for_bits(bits_len):
    return 2 ** bits_len
