import weakref
import collections.abc


class WeakKeyDefaultDictionary(collections.abc.MutableMapping):
    """a defaultdict-like class but which holds weak references to its keys.

    Note some differences:
    WeakKeyDefaultDictionary's constructor function takes one argument (the missing key).
    So `wkdd = WeakKeyDefaultDictionary(lambda k: [])` rather than `defaultdict(list)`
    """

    def __init__(
        self,
        ctor,
        pairs=(),
        /,
        **kwargs,
    ):
        self._d = {}
        self._ctor = ctor

        for (
            k,
            v,
        ) in pairs:
            self[k] = v

        for (
            k,
            v,
        ) in kwargs.items():
            self[k] = v

    def _autoremove(self, k):
        del self[k]

    def __setitem__(self, k, v):
        self._d[
            weakref.ref(
                k,
                self._autoremove,
            )
        ] = v

    def __getitem__(self, k):
        return self._d[weakref.ref(k)]

    def __delitem__(self, k):
        del self._d[weakref.ref[k]]

    def __iter__(
        self,
    ):
        """gives an iterator of strong references to keys"""
        yield from (k() for k in self._d)

    def __len__(
        self,
    ):
        """the current length of the dictionary

        Note that subsequent len()s might not be stable, as background garbage collection can change the size
        """
        return len(self._d)
