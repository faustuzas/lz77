class ListDataLoader:

    def __init__(self, arr):
        self.arr = [a for a in arr]

    def __next__(self):
        if len(self.arr) == 0:
            raise StopIteration()

        return self.arr.pop(0)

    def __iter__(self):
        return self
