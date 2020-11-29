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


def offset_to_bytes(offset):
    try:
        return offset.to_bytes(2, byteorder='big', signed=False)
    except OverflowError:
        print('a')


def bytes_to_offset(bytes_source):
    bytes_ = bytes()
    for _ in range(2):
        bytes_ += next(bytes_source)
    return int.from_bytes(bytes_, byteorder='big', signed=False)


def match_length_to_bytes(match_length):
    return match_length.to_bytes(1, byteorder='big', signed=False)


def bytes_to_match_length(bytes_source):
    return int.from_bytes(next(bytes_source), byteorder='big', signed=False)


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

    def __init__(self, file_handle):
        self._file_handle = file_handle

    def ingest(self, el):
        self._file_handle.write(bytes(el))


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
