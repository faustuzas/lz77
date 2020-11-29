class DecodingSearchBuffer:

    def __init__(self, capacity) -> None:
        self._arr = [None] * capacity
        self._size = 0
        self._capacity = capacity

    def push(self, el) -> None:
        self._arr.pop(0)
        self._arr.append(el)

    def peek_by_lz_offset(self, lz_offset):
        return self._arr[self._capacity - lz_offset]

    def __str__(self) -> str:
        return str(self._arr)


class LZ77Decoder:

    def __init__(self, data_loader, result_ingestor, search_buff_size):
        self._data_loader = data_loader
        self._result_ingestor = result_ingestor
        self._search_buff = DecodingSearchBuffer(search_buff_size)

    def decode(self):
        for triplet in self._data_loader:
            for i in range(triplet.match_length):
                el = self._search_buff.peek_by_lz_offset(triplet.offset)
                self._record_decoded_el(el)

            self._record_decoded_el(triplet.el)

    def _record_decoded_el(self, el):
        self._search_buff.push(el)
        self._result_ingestor.ingest(el)
