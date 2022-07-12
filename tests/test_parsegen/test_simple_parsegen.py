import io

from textwrap import dedent
from typing import Callable

from rattle.parsegen.grammar import (
    grammar,
    Grammar,
    GrammarExp,
    Alt,
    NT,
    T,
)

from rattle.parsegen.token_info import TokenType, SourceInfo, Token
from rattle.parsegen.tokenizer import tokenize, default_tree
from rattle.parsegen.parser import Parser
from rattle.parsegen.pretty_printer import GrammarPrinter

from .parser_helpers import assert_parses_to


@grammar
class SimpleGrammar1:
    start_symbol = "S"

    S = NT("A").as_alt().as_rhs()
    A = T(Token(TokenType.IDENT)).as_alt().as_rhs()


def test_parse_sg1():
    assert_parses_to(
        SimpleGrammar1,
        "a",
        Token(TokenType.IDENT, "a", SourceInfo("<unknown>", (0, 0), (0, 1))),
    )


def test_pprint_sg1():
    f = io.StringIO()
    GrammarPrinter().pretty_print(SimpleGrammar1, f)
    assert f.getvalue() == dedent(
        """\
        @tokens := {
            IDENT=0,
            STRING=1,
            NUMBER=2
        };

        @start_symbol := S;

        A := IDENT;
        S := A;
        """
    )


@grammar
class SimpleGrammarAction:
    start_symbol = "S"

    S = T("A", "a").as_alt(action="[a]").as_rhs()
    A = T(Token(TokenType.IDENT)).as_alt().as_rhs()


def test_parse_sgaction():
    assert_parses_to(
        SimpleGrammarAction,
        "a",
        [Token(TokenType.IDENT, "a", SourceInfo("<unknown>", (0, 0), (0, 1)))],
    )
