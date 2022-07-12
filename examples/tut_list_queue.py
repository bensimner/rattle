import pytest

from rattle import R


@R.check
class Queue:
    ghost_data = R.ghost.attr(default_factory=list)

    def __init__(self, elems=()):
        self._q = []
        self.extend(elems)

    def enqueue(self, v):
        self._q.append(v)

    def dequeue(self):
        return self._q.pop(0)

    def extend(self, elems):
        for e in elems:
            self.enqueue(e)


def test_queue():
    q = Queue([1, 2, 3])
    q.enqueue(1)
    q.enqueue(2)
    q.dequeue()
    R.reject(lambda: q.dequeue() == 2)


if __name__ == "__main__":
    test_queue()
