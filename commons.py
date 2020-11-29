class LZ77Triple:

    def __init__(self, offset, match_length, el) -> None:
        self.offset = offset
        self.match_length = match_length
        self.el = el

    def __str__(self):
        return f'({self.offset}, {self.match_length}, {self.el})'

    def __repr__(self):
        return str(self)

    def __bytes__(self):
        return offset_to_bytes(self.offset) + match_length_to_bytes(self.match_length) + el_to_bytes(self.el)


offset_size_in_bytes = 1
match_len_size_in_bytes = 1


def offset_to_bytes(offset):
    return int_to_bytes(offset, offset_size_in_bytes)


def bytes_to_offset(bytes_source):
    return bytes_to_int(bytes_source, offset_size_in_bytes)


def match_length_to_bytes(match_length):
    return int_to_bytes(match_length, match_len_size_in_bytes)


def bytes_to_match_length(bytes_source):
    return bytes_to_int(bytes_source, match_len_size_in_bytes)


def int_to_bytes(num, bytes_count):
    return num.to_bytes(bytes_count, byteorder='big', signed=False)


def bytes_to_int(bytes_source, bytes_count):
    bytes_ = bytes()
    for _ in range(bytes_count):
        bytes_ += next(bytes_source)
    return int.from_bytes(bytes_, byteorder='big', signed=False)


def el_to_bytes(el):
    converted = bytes(el)
    if len(converted) != 1:
        raise ValueError('Encrypted element should be of length 1')
    return converted


class ListDataIngestor:

    def __init__(self):
        self._arr = []

    def ingest(self, el):
        self._arr.append(el)

    def result(self):
        return self._arr


class FileIngestor:

    def __init__(self, file_name):
        self._file_name = file_name
        self._fd = None

    def __enter__(self):
        self._fd = open(self._file_name, 'wb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fd.close()

    def ingest(self, el):
        self._fd.write(bytes(el))


def list_data_loader(arr):
    arr = [a for a in arr]
    for el in arr:
        yield el


def file_byte_data_loader(file_name):
    with open(file_name, 'rb') as f:
        while True:
            byte = f.read(1)
            if not byte:
                return
            yield byte


def triplet_decoder(binary_source):
    while True:
        try:
            offset = bytes_to_offset(binary_source)
            match_length = bytes_to_match_length(binary_source)
            el = next(binary_source)
            yield LZ77Triple(offset, match_length, el)
        except StopIteration:
            return None
