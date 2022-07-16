import re
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import deque
from tokenize import Token

from rattle.errors import TokenizeError
from rattle.utils.itertools import (
    find_exactly_one,
)

from rattle.logging import get_logger

logger = get_logger(__name__)


@dataclass
class StepResult:
    token_type: object
    next: object | None
    consumed: int
    converted: str


@dataclass
class RegexEntry:
    pattern: str
    token_type: object
    next: object | None

    def step(self, key: str) -> StepResult | None:
        m = re.search(self.pattern, key)
        if m is not None:
            s = m.group(0)
            consumed = len(s)
            return StepResult(self.token_type, self.next, consumed, s)
        else:
            return None

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self is other


def _attach_next(tree: "PrefixTree", next: "PrefixTree", seen: "set[PrefixTree] | None" = None) -> None:
    """Ensure all paths in tree are followed by `next`"""
    if seen is None:
        seen = set()

    for e in tree.tree:
        if e in seen:
            continue

        seen.add(e)

        if e.next is None:
            e.next = next
        else:
            _attach_next(e.next, next, seen=seen)


@dataclass
class PrefixTree:
    """A hierarchical prefix tree"""

    name: str
    token_type: object | None = None
    tree: list = field(default_factory=list)

    def __post_init__(self):
        if self.name is None:
            raise ValueError("name cannot be None")

    def insert_step_regex(self, key_pattern, value, next=None, next_name=None) -> "PrefixTree":
        if next is None:
            next = PrefixTree(next_name)

        self.tree.append(RegexEntry(key_pattern, value, next))

        return next

    def insert_step_tree(self, tree: "PrefixTree", next=None, next_name=None, converter=None) -> "PrefixTree":
        if next is None:
            next = PrefixTree(next_name)

        _attach_next(tree, next)
        self.tree.extend(tree.tree)

        return next

    def insert_word(self, key, value) -> None:
        cur = self
        for c in key[:-1]:
            try:
                r = self.step(cur, c)
                cur = r.next
            except TokenizeError:
                cur = cur.insert_step_regex(re.escape(c), None, next_name=f"tok_{key}_post_{c}")
        # separate out -1 case, as it needs to tag with the `value`
        # but not the previous ones!
        cur.insert_step_regex(re.escape(key[-1]), value, None, next_name=f"post_{key}-deadend")

    def step(self, tree, key) -> StepResult:
        for e in tree.tree:
            r = e.step(key)
            if r is not None:
                return r
        raise TokenizeError(f"unknown symbol {key!r}")

    def split_prefix(self, s: str):
        with logger.start("split_prefix", level=logger.level.IN_TESTS, s=s, tree=self.name) as ctx:

            cur = self
            consumed = 0
            r = None

            for c in s:
                ctx.add_message("try_char", c=c, tree=cur.name)

                try:
                    r = self.step(cur, c)
                except TokenizeError:
                    break
                else:
                    ctx.add_message("stepped", r=r)
                    assert isinstance(r, StepResult)
                    consumed += r.consumed
                    cur = r.next

            if not isinstance(r, StepResult):
                raise TokenizeError()

            tok_src = s[:consumed]  # not including `i`
            r = (tok_src, r.token_type, s[consumed:])
            ctx.add_success_field(r=r)
            return r
