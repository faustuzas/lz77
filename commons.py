class LZ77Triple:

    def __init__(self, offset, match_length, el) -> None:
        self.offset = offset
        self.match_length = match_length
        self.el = el

    def __str__(self):
        return f'({self.offset}, {self.match_length}, {self.el})'

    def __repr__(self):
        return str(self)