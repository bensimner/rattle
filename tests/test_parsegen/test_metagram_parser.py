import io

from rattle.parsegen import grammar
from rattle.parsegen.token_info import Token
from rattle.parsegen.metagram import MetaGram

from .tokenizer_helpers import TokenEnumEq, assert_tokenizes_to
from .parser_helpers import assert_parses, assert_parses_to, assert_not_parses

EXAMPLE_GRAM1 = """\
@tokens := {
    A=";",
};

@start_symbol := X;

X := Z;
"""


def test_tokenize_gram1():
    assert_tokenizes_to(
        MetaGram,
        EXAMPLE_GRAM1,
        [
            Token(MetaGram.tokens.IDENT, "@tokens"),
            Token(MetaGram.tokens.ASSIGN),
            Token(MetaGram.tokens.LBRACE),
            Token(MetaGram.tokens.IDENT, "A"),
            Token(MetaGram.tokens.EQ),
            Token(MetaGram.tokens.STRING, '";"'),
            Token(MetaGram.tokens.COMMA),
            Token(MetaGram.tokens.RBRACE),
            Token(MetaGram.tokens.SEMICOLON),
            Token(MetaGram.tokens.IDENT, "@start_symbol"),
            Token(MetaGram.tokens.ASSIGN),
            Token(MetaGram.tokens.IDENT, "X"),
            Token(MetaGram.tokens.SEMICOLON),
            Token(MetaGram.tokens.IDENT, "X"),
            Token(MetaGram.tokens.ASSIGN),
            Token(MetaGram.tokens.IDENT, "Z"),
            Token(MetaGram.tokens.SEMICOLON),
        ],
    )


def test_parse_gram1():
    tokens = [("A", ";")]
    rules = [grammar.Rule("X", grammar.Rhs([grammar.Alt(grammar.Atom(None, "Z"))]))]
    assert_parses_to(
        MetaGram,
        EXAMPLE_GRAM1,
        grammar.Grammar(
            header=None,
            start_symbol="X",
            tokens=TokenEnumEq(tokens),
            rules=rules,
        ),
    )


def test_parse_gram_empty_rule():
    assert_not_parses(
        MetaGram,
        ":=",
    )
