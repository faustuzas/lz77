from utils import LZ77Triple

search_buff_size = 7
raw_triplets = [(0, 0, 'c'), (0, 0, 'a'), (0, 0, 'b'), (0, 0, 'r'), (4, 3, 'r')]
triplets = [LZ77Triple(*x) for x in raw_triplets]


class ArrayDataLoader:

    def __init__(self, arr):
        self.arr = [a for a in arr]

    def __next__(self):
        if len(self.arr) == 0:
            raise StopIteration()

        return self.arr.pop(0)

    def __iter__(self):
        return self


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


data_loader = ArrayDataLoader(triplets)
search_buff = DecodingSearchBuffer(search_buff_size)
result = []

for triplet in data_loader:
    for i in range(triplet.match_length):
        el = search_buff.peek_by_lz_offset(triplet.offset)
        result.append(el)
        search_buff.push(el)

    result.append(triplet.codeword)
    search_buff.push(triplet.codeword)

print(result)