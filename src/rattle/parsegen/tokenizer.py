import re
import string
import itertools

from rattle.errors import (
    TokenizeError,
)
from rattle.parsegen import (
    token_info,
)
from rattle.utils.prefixtree import (
    PrefixTree,
)

from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        IO,
        Iterator,
    )


def build_prefix_tree(
    toks,
):
    token_tree = PrefixTree()

    # build up the symbols
    for t in toks.members():
        if isinstance(
            t.value,
            str,
        ):
            token_tree.insert(
                t.value,
                t,
            )

    # add IDENT
    subtree = token_tree.insert_step(
        "[@a-zA-Z]",
        token_info.TokenType.IDENT,
    )
    subtree.insert_step(
        r"[a-zA-Z0-9_]",
        token_info.TokenType.IDENT,
        new=subtree,
    )

    # add NUMBER
    subtree = token_tree.insert_step(
        "[0-9]",
        token_info.TokenType.NUMBER,
    )
    subtree.insert_step(
        r"[0-9_]",
        token_info.TokenType.NUMBER,
        new=subtree,
    )

    # add STRING
    subtree = token_tree.insert_step('["]', None)
    # empty string
    subtree.insert_step(
        '["]',
        token_info.TokenType.STRING,
    )
    # non-empty string
    subtree = subtree.insert_step('[^"]', None)
    subtree = subtree.insert_step(
        '[^"]',
        None,
        new=subtree,
    )
    subtree.insert_step(
        '["]',
        token_info.TokenType.STRING,
    )

    return token_tree


def tokenize(
    src: "IO[str]",
    *,
    filename: str,
    token_tree: PrefixTree,
) -> "Iterator[token_info.Token]":
    # inefficient, but works
    s = src.read()

    lineno = 0
    col = 0

    while s:
        (
            tok_src,
            tok_type,
        ), s = token_tree.split_prefix(s)

        start = (
            lineno,
            col,
        )
        lineno += tok_src.count("\n")
        if "\n" in tok_src:
            col = 0
        col += len(tok_src.rpartition("\n")[-1])
        stop = (
            lineno,
            col,
        )
        sinfo = token_info.SourceInfo(
            filename,
            start,
            stop,
        )

        # if tok_type is None then either we failed to tokenize or we hit some whitespace
        if tok_type is None:
            if s[0] in "\n ":
                s = s[1:]
            else:
                raise TokenizeError(f"failed to tokenize {start}->{stop} {tok_src!r}")
        else:
            yield token_info.Token(
                tok_type,
                tok_src,
                sinfo,
            )


default_tree = build_prefix_tree(token_info.TokenType)
