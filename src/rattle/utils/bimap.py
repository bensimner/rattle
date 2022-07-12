import collections.abc


class Bimap(collections.abc.MutableMapping):
    """a bidirectional dict-like class"""

    def __init__(
        self,
        mapping_or_pairs=(),
        /,
        **kwargs,
    ):
        self._l2r = {}
        self._r2l = {}

        try:
            ks = mapping_or_pairs.keys()
        except AttributeError:
            for (
                k,
                v,
            ) in mapping_or_pairs:
                self[k] = v
        else:
            for k in ks:
                self[k] = mapping_or_pairs[k]

        for (
            k,
            v,
        ) in kwargs.items():
            self[k] = v

    def __setitem__(self, k, v):
        self._l2r[k] = v
        self._r2l[v] = k

    def __getitem__(self, k):
        try:
            return self._l2r[k]
        except KeyError:
            return self._r2l[k]

    def __delitem__(self, k):
        try:
            v = self._l2r.pop(k)
            del self._r2l[v]
        except KeyError:
            v = self._r2l.pop(k)
            del self._l2r[v]

    def __iter__(
        self,
    ):
        yield from self._l2r

    def __len__(
        self,
    ):
        return len(self._l2r)
