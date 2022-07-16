import io
import importlib.resources

from hypothesis import given, strategies as st

from rattle.parsegen.grammar import (
    Grammar,
    Rule,
    Rhs,
    Alt,
    Boxed,
    Optional,
    Sequence,
    Star,
    Atom,
    NT,
    T,
)

from rattle.parsegen import token_info
from rattle.parsegen.pretty_printer import GrammarPrinter
from rattle.parsegen.metagram import MetaGram

from .parser_helpers import assert_parses_to


def test_metagram_roundtrip():
    f = importlib.resources.open_text("rattle.parsegen", "metagram.gram")
    ast = MetaGram.parse(f, "metagram.gram")
    print(ast)
    assert False
