from utils import LZ77Triple

input_stream = ['c', 'a', 'b', 'r', 'a', 'c', 'a', 'd', 'a', 'b', 'r', 'a', 'r', 'r', 'a', 'r', 'r', 'a', 'd']

look_ahead_buff_size = 6
search_buff_size = 7


class ArrayDataLoader:

    def __init__(self, arr):
        self.arr = [a for a in arr]

    def __next__(self):
        if len(self.arr) == 0:
            raise StopIteration()

        return self.arr.pop(0)

    def __iter__(self):
        return self


class EncodingArray:

    def __init__(self, data_loader, search_buff_size, look_ahead_buff_size):
        self._data_loader = data_loader
        self._search_buff_size = search_buff_size
        self._look_ahead_buff_size = look_ahead_buff_size

        self._arr = [None] * (search_buff_size + look_ahead_buff_size)
        self._head_offset = search_buff_size
        self._is_data_loader_empty = False

    def _read_from_loader(self):
        if self._is_data_loader_empty:
            return None

        try:
            return next(self._data_loader)
        except StopIteration:
            self._is_data_loader_empty = True
            return None

    def head_el(self):
        return self._arr[self._head_offset]

    def peek(self, offset_from_head):
        return self._arr[self._head_offset + offset_from_head]

    def move_head(self, offset):
        for i in range(offset):
            self._arr.pop(0)
            self._arr.append(self._read_from_loader())

    def init_look_ahead(self):
        self._arr[self._look_ahead_buff_size + 1:] = [
            self._read_from_loader()
            for _ in range(self._look_ahead_buff_size)
        ]

    def lz_offsets_in_search_buff(self, el):
        offsets = []
        last_index = 0
        try:
            while True:
                last_index = self._arr.index(el, last_index + 1, search_buff_size)
                offsets.append(search_buff_size - last_index)
        except ValueError:
            return offsets


enc_arr = EncodingArray(ArrayDataLoader(input_stream), search_buff_size, look_ahead_buff_size)
enc_arr.init_look_ahead()

result = []

while True:
    head = enc_arr.head_el()
    if head is None:
        break

    lz_offsets = enc_arr.lz_offsets_in_search_buff(head)
    if len(lz_offsets) == 0:
        lz_offset = 0
        result.append(LZ77Triple(lz_offset, 0, head))

    enc_arr.move_head(lz_offset + 1)

