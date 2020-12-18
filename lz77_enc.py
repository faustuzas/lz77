from commons import LZ77Triplet


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

    def find_lz_offsets_in_search_buff(self, el):
        offsets = []
        last_found_index = 0
        try:
            while True:
                # search for next occurrence of the element, skipping `last_found_index` elements
                # because in the next iteration we want to skip just found element, we add +1 to the end
                last_found_index = self._arr.index(el, last_found_index, self._search_buff_size) + 1

                # we are working with LZ offsets, which are counter from the head, not from the start of array
                offsets.append(self._head_offset - last_found_index + 1)

        # index function will throw ValueError when it cannot find an occurrence of the element
        except ValueError:
            return offsets

    def peek_by_lz_offset(self, lz_offset):
        return self._arr[self._head_offset - lz_offset]


class LZ77Encoder:

    def __init__(self, data_loader, result_ingestor, search_buff_size, look_ahead_buff_size):
        self._result_ingestor = result_ingestor

        self._look_ahead_buff_size = look_ahead_buff_size
        self._enc_arr = LZ77EncodingArray(data_loader, search_buff_size, look_ahead_buff_size)

    @staticmethod
    def _find_best_match(triplets):
        # find what was the longest match
        longest_match = max(map(lambda x: x.match_length, triplets), default=1)

        # filter all triplets that have a match of the longest match
        best_matches = filter(lambda x: x.match_length == longest_match, triplets)

        # if there are several triplets with the same match length, pick with the least offset
        return min(best_matches, key=lambda x: x.offset)

    def encode(self):
        self._enc_arr.init_look_ahead()

        while True:
            head = self._enc_arr.head_el()
            if head is None:
                break

            # find all occurrences of the element in the search buffer and their offsets
            # to avoid heavy computation, take only 10 offsets
            lz_offsets = self._enc_arr.find_lz_offsets_in_search_buff(head)

            if len(lz_offsets) == 0:
                # no occurrences are found, just add the element
                triplet = LZ77Triplet(0, 0, head)
            else:
                # iterate through found offsets and check what matches we can get
                found_triplets = []
                for lz_offset in lz_offsets:
                    match_len = 1
                    look_ahead_el = head
                    match_finished = True
                    for i in range(1, self._look_ahead_buff_size):
                        search_el = self._enc_arr.peek_by_lz_offset(lz_offset - i)
                        look_ahead_el = self._enc_arr.peek_in_look_ahead(i)

                        if search_el != look_ahead_el:
                            match_finished = True
                            break
                        else:
                            match_len += 1
                            match_finished = False

                    # there could be a case, where matching is not finished when look ahead buffer is depleted
                    # to be able to form a proper triplet, we reduce match length by one
                    # and treat the last letter as not found
                    if not match_finished:
                        match_len -= 1

                    found_triplets.append(LZ77Triplet(lz_offset, match_len, look_ahead_el))

                    # if we have found a longest possible match, stop the search, we cannot find better
                    if match_len in (self._look_ahead_buff_size - 1, self._look_ahead_buff_size):
                        break

                # find which of the found matches has the longest match length - which is the best match
                triplet = self._find_best_match(found_triplets)

                # the last triplet might have a None value, fix it so the encoding would be a proper one
                if triplet.el is None:
                    match_len = triplet.match_length - 1
                    if match_len == 0:
                        # if the match length is zero, set offset to zero as well to avoid confusion
                        triplet = LZ77Triplet(0, 0, head)
                    else:
                        # go back one matched element and treat it as "not found"
                        triplet = LZ77Triplet(triplet.offset, match_len, self._enc_arr.peek_in_look_ahead(match_len))

            # move the head by matched length and additional one, because last letter was marked as "not found"
            self._enc_arr.move_head(triplet.match_length + 1)

            # consume the found triplet
            self._result_ingestor.ingest(triplet)
