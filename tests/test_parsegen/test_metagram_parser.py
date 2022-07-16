import io

from rattle.parsegen import grammar
from rattle.parsegen.token_info import Token
from rattle.parsegen.metagram import MetaGram

from .tokenizer_helpers import TokenEnumEq, assert_tokenizes_to
from .parser_helpers import assert_parses, assert_parses_to, assert_not_parses


GRAM_NO_HEADERS = """\
X := Z;
"""


def test_tokenize_gram_no_headers():
    assert_tokenizes_to(
        MetaGram,
        GRAM_NO_HEADERS,
        [
            Token(MetaGram.tokens.IDENT, "X"),
            Token(MetaGram.tokens.ASSIGN),
            Token(MetaGram.tokens.IDENT, "Z"),
            Token(MetaGram.tokens.SEMICOLON),
        ],
    )


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
    rules = {"X": grammar.Rule("X", grammar.Rhs([grammar.Alt(grammar.Atom(None, "Z"))]))}
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
