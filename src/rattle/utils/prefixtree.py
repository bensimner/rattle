import re

from rattle.utils.itertools import (
    find_exactly_one,
)


class PrefixTree:
    """A prefix tree"""

    def __init__(
        self,
    ):
        self._value = None
        self._tree = {}

    def insert(
        self,
        key,
        value,
        new=None,
    ):
        if key == "":
            if self._value is not None and self._value != value:
                raise ValueError("duplicate key")
            self._value = value
            return

        c = key[0]
        c = re.escape(c)

        try:
            v = self._tree[c]
        except KeyError:
            if new is None:
                new = PrefixTree()
            v = self._tree[c] = new

        v.insert(
            key[1:],
            value,
        )

    def insert_step(
        self,
        c_pattern,
        value,
        new=None,
    ):
        try:
            self._tree[c_pattern]
        except KeyError:
            if new is None:
                new = PrefixTree()
            v = self._tree[c_pattern] = new
            v._value = value
        else:
            raise ValueError(f"duplicate key: {c_pattern}")

        return v

    def step(self, c):
        try:
            k = find_exactly_one(
                k
                for k in self._tree
                if re.fullmatch(
                    k,
                    c,
                )
            )
        except ValueError:
            raise KeyError(c) from None

        return self._tree[k]

    def split_prefix(self, s):
        """given a string, follow the tree and return (token, remaining)"""
        if s == "":
            return None

        i = 0

        tree = self
        while i < len(s):
            c = s[i]

            try:
                tree = tree.step(c)
            except KeyError:
                # woo, finished a token!
                tok_src = s[:i]  # not including `i`
                return (
                    (
                        tok_src,
                        tree._value,
                    ),
                    s[i:],
                )
            else:
                i += 1

        #  we (possibly) found a token!
        # note that it might not be a valid token if tree._value is None.
        tok_src = s  # and, the whole string was a single token
        return (
            (
                tok_src,
                tree._value,
            ),
            "",
        )

    def pprint(
        self,
    ):
        lines = []
        lines.append(f"- {self._value!r}")
        seen = set()
        seen.add(self)
        for (
            k,
            v,
        ) in self._tree.items():
            if v in seen:
                s = "[..]"
            else:
                s = v.pprint()
            seen.add(v)
            sublines = s.splitlines()
            lines.append(f"|- {k!r}")
            sublines = ["  " + line for line in sublines]
            lines.extend(sublines)
        return "\n".join(lines)
