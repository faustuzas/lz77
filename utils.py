class RingBuffer:

    def __init__(self, capacity) -> None:
        self._arr = [None] * capacity
        self._size = 0
        self._capacity = capacity

    def push(self, el) -> None:
        self._arr.pop(0)
        self._arr.append(el)

    def index_of(self, el):
        try:
            return self._capacity - self._arr.index(el)
        except ValueError:
            return -1

    def __getitem__(self, item):
        return self._arr[item]

    def __str__(self) -> str:
        return str(self._arr)


class LZ77Triple:

    def __init__(self, offset, match_length, codeword) -> None:
        self.offset = offset
        self.match_length = match_length
        self.codeword = codeword

    def __str__(self):
        return f'({self.offset}, {self.match_length}, {self.codeword})'

    def __repr__(self):
        return str(self)