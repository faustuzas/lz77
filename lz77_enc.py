from commons import LZ77Triple


class LZ77EncodingArray:

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
        self._arr[self._search_buff_size:] = [
            self._read_from_loader()
            for _ in range(self._look_ahead_buff_size)
        ]

    def lz_offsets_in_search_buff(self, el):
        offsets = []
        last_index = 0
        try:
            while True:
                last_index = self._arr.index(el, last_index, self._search_buff_size) + 1
                offsets.append(self._head_offset - last_index + 1)
        except ValueError:
            return offsets

    def peek_by_lz_offset(self, lz_offset):
        return self._arr[self._head_offset - lz_offset]


class LZ77Encoder:

    def __init__(self, data_loader, result_ingestor, search_buff_size, look_ahead_buff_size):
        self._search_buff_size = search_buff_size
        self._look_ahead_buff_size = look_ahead_buff_size

        self._result_ingestor = result_ingestor
        self._enc_arr = LZ77EncodingArray(data_loader, search_buff_size, look_ahead_buff_size)

    @staticmethod
    def _find_best_match(matches):
        longest_match = max(map(lambda x: x.match_length, matches), default=1)
        best_matches = filter(lambda x: x.match_length == longest_match, matches)
        return min(best_matches, key=lambda x: x.offset)

    def encode(self):
        self._enc_arr.init_look_ahead()

        while True:
            head = self._enc_arr.head_el()
            if head is None:
                break

            lz_offsets = self._enc_arr.lz_offsets_in_search_buff(head)
            if len(lz_offsets) == 0:
                triplet = LZ77Triple(0, 0, head)
            else:
                found_triplets = []
                for lz_offset in lz_offsets:
                    match_len = 1
                    look_ahead_el = head
                    for i in range(1, self._look_ahead_buff_size):
                        search_el = self._enc_arr.peek_by_lz_offset(lz_offset - i)
                        look_ahead_el = self._enc_arr.peek_in_look_ahead(i)

                        if search_el != look_ahead_el:
                            break
                        else:
                            match_len += 1
                    found_triplets.append(LZ77Triple(lz_offset, match_len, look_ahead_el))

                triplet = self._find_best_match(found_triplets)

                # fix the last triplet so it would not contain None value
                if triplet.el is None:
                    match_len = triplet.match_length - 1
                    triplet = LZ77Triple(triplet.offset, match_len, self._enc_arr.peek_in_look_ahead(match_len))

            self._enc_arr.move_head(triplet.match_length + 1)
            self._result_ingestor.ingest(triplet)

