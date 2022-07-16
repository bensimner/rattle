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
from rattle.logging import get_logger

from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        IO,
        Iterator,
    )

logger = get_logger(__name__)


def _add_COMMENT(token_tree: PrefixTree):
    # add line comments
    subtree = token_tree.insert_step_regex("#", token_info.SKIP, next_name="start-comment")
    subtree = subtree.insert_step_regex(r".", token_info.SKIP, next_name="cont-comment")
    subtree.insert_step_regex(r".", token_info.SKIP, next=subtree)


def _add_WHITESPACE(token_tree: PrefixTree):
    token_tree.insert_step_regex(r"\s", token_info.SKIP, next_name="whitespace-deadend")


def _add_IDENT(token_tree: PrefixTree):
    # add IDENT
    subtree = token_tree.insert_step_regex("[@a-zA-Z]", token_info.TokenType.IDENT, next_name="ident_tail")
    subtree.insert_step_regex(
        r"[a-zA-Z0-9_]",
        token_info.TokenType.IDENT,
        next=subtree,
    )


def _add_NUMBER(token_tree: PrefixTree):
    # add NUMBER
    subtree = token_tree.insert_step_regex(
        "[0-9]",
        token_info.TokenType.NUMBER,
        next_name="number-cont",
    )
    subtree.insert_step_regex(
        r"[0-9_]",
        token_info.TokenType.NUMBER,
        next=subtree,
    )


def convert_esc_seq(esc):
    return esc


def _add_STRING_ESC(token_tree: PrefixTree):
    esc_tree = PrefixTree("string_escape_seq")
    subtree = esc_tree.insert_step_regex(r"\\", None, next_name="string-esc-cont")
    subtree.insert_step_regex(r"[\\nt]", token_info.TokenType.STRING, next=token_tree)


def _add_STRING(token_tree: PrefixTree):
    # add STRING
    string_body = PrefixTree("string_body")

    token_tree.insert_step_regex('["]', None, next=string_body, next_name="string_body")

    # close quote
    string_body.insert_step_regex(
        '["]',
        token_info.TokenType.STRING,
        next_name="string-end-deadend",
    )

    # char
    string_body.insert_step_regex(
        r'[^"\\]',
        None,
        next=string_body,
    )

    # esc sequence
    _add_STRING_ESC(string_body)


def build_prefix_tree(
    toks,
):
    token_tree = PrefixTree("root")

    # build up the symbols
    for t in toks.members():
        if isinstance(
            t.value,
            str,
        ):
            token_tree.insert_word(
                t.value,
                t,
            )

    _add_IDENT(token_tree)
    _add_NUMBER(token_tree)
    _add_STRING(token_tree)
    _add_COMMENT(token_tree)
    _add_WHITESPACE(token_tree)

    return token_tree


def tokenize(
    src: "IO[str]",
    *,
    filename: str,
    token_tree: PrefixTree,
) -> "Iterator[token_info.Token]":
    with logger.start("tokenize", filename=filename) as ctx:
        # inefficient, but works
        s = src.read()

        lineno = 0
        col = 0

        while s:
            (tok_src, tok_type, s) = token_tree.split_prefix(s)

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
                raise TokenizeError(f"failed to tokenize {start}->{stop} {tok_src!r}")
            elif tok_type is token_info.SKIP:
                continue
            else:
                tok = token_info.Token(
                    tok_type,
                    tok_src,
                    sinfo,
                )
                ctx.add_message("got", tok=tok)
                yield tok


default_tree = build_prefix_tree(token_info.TokenType)
