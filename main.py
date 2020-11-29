from utils import RingBuffer, LZ77Triple

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


class LookAheadBuffer:

    def __init__(self, capacity, data_loader):
        self._capacity = capacity
        self._arr = []

        self._data_loader = data_loader
        self._is_data_loader_empty = False

        for i in range(capacity):
            loaded = self._load_el()
            if not loaded:
                break

    def _load_el(self):
        if self._is_data_loader_empty:
            return False

        try:
            self._arr.append(next(self._data_loader))
            return True
        except StopIteration:
            self._is_data_loader_empty = True
            return False

    def peek(self, i):
        if i >= self._capacity:
            return None
        return self._arr[i]

    def index_of(self, el):
        try:
            return self._arr.index(el)
        except ValueError:
            return -1

    def iterate_with_loading(self):
        while len(self._arr) != 0:
            el = self._arr.pop(0)
            self._load_el()
            yield el

    def iterate_current_snapshot(self):
        for el in self._arr:
            yield el

    def __str__(self):
        return str(self._arr)


if __name__ == "__main__":
    look_ahead_buff = LookAheadBuffer(look_ahead_buff_size, ArrayDataLoader(input_stream))
    search_buff = RingBuffer(search_buff_size)
    result = []

    for c in look_ahead_buff.iterate_with_loading():
        idx = search_buff.index_of(c)
        if idx == -1:
            result.append(LZ77Triple(0, 0, c))
            search_buff.push(c)
            continue

        for el in look_ahead_buff.iterate_current_snapshot():
            look_ahead_buff.peek()

        print('a')