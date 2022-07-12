from itertools import (
    count,
)
from collections.abc import (
    Sequence,
)


class IndexedStream(Sequence):
    def __init__(self, stream):
        self._stop = 0
        self._stream = iter(stream)
        self._eof = False
        self._elems = []

    def _unwind_upto(self, idx):
        while idx >= self._stop:
            try:
                self._elems.append(next(self._stream))
            except StopIteration:
                self._eof = True
                raise IndexError(idx) from None
            else:
                self._stop += 1

    def __getitem__(self, i):
        self._unwind_upto(i)
        return self._elems[i]

    def __iter__(
        self,
    ):
        for i in count():
            try:
                yield self[i]
            except IndexError:
                return

    def __len__(
        self,
    ):
        if not self._eof:
            raise ValueError("Cannot get length of an unfinished stream")
        else:
            return self._stop

    def at_eof(
        self,
    ):
        return self._eof
