from utils import LZ77Triple

input_stream = [

]

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

    def peek_in_look_ahead(self, offset_from_head):
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
                last_index = self._arr.index(el, last_index, search_buff_size) + 1
                offsets.append(self._head_offset - last_index + 1)
        except ValueError:
            return offsets

    def peek_by_lz_offset(self, lz_offset):
        return self._arr[self._head_offset - lz_offset]


def find_best_match(matches):
    longest_match = max(map(lambda x: x.match_length, matches), default=1)
    best_matches = filter(lambda x: x.match_length == longest_match, matches)
    return min(best_matches, key=lambda x: x.offset)


enc_arr = EncodingArray(ArrayDataLoader(input_stream), search_buff_size, look_ahead_buff_size)
enc_arr.init_look_ahead()

result = []

for i in range(1, 1000000):
    head = enc_arr.head_el()
    if head is None:
        break

    lz_offsets = enc_arr.lz_offsets_in_search_buff(head)
    if len(lz_offsets) == 0:
        triple = LZ77Triple(0, 0, head)
    else:
        found_triplets = []
        for lz_offset in lz_offsets:
            match_len = 1
            look_ahead_el = head
            for i in range(1, look_ahead_buff_size):
                search_el = enc_arr.peek_by_lz_offset(lz_offset - i)
                look_ahead_el = enc_arr.peek_in_look_ahead(i)

                if search_el != look_ahead_el:
                    break
                else:
                    match_len += 1
            found_triplets.append(LZ77Triple(lz_offset, match_len, look_ahead_el))

        triple = find_best_match(found_triplets)
        if triple.codeword is None:
            match_len = triple.match_length - 1
            triple = LZ77Triple(triple.offset, match_len, enc_arr.peek_in_look_ahead(match_len))

    result.append(triple)

    enc_arr.move_head(triple.match_length + 1)

print(result)
