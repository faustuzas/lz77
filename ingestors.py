class ListDataIngestor:

    def __init__(self):
        self._arr = []

    def ingest(self, el):
        self._arr.append(el)

    def result(self):
        return self._arr
