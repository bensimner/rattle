import io

from rattle.parsegen.token_info import Token
from rattle.rat.parse.tokens import RatTokens, rat_tree

from ...test_parsegen.tokenizer_helpers import assert_tokenizes_to


def test_tokenize_single_symbol():
    assert_tokenizes_to(None, ";", [Token(RatTokens.SEMICOLON)], default_token_tree=rat_tree)
    assert_tokenizes_to(None, "(", [Token(RatTokens.LPAREN)], default_token_tree=rat_tree)


def test_tokenize_single_symbol_multichar():
    assert_tokenizes_to(None, ":=", [Token(RatTokens.ASSIGN)], default_token_tree=rat_tree)


EXAMPLE1 = """\
a := 1;
fn {
    a := 42;
    @v := alloc(

    );
}
"""


def test_tokenize_example1():
    assert_tokenizes_to(
        None,
        EXAMPLE1,
        [
            Token(RatTokens.IDENT, "a"),
            Token(RatTokens.ASSIGN),
            Token(RatTokens.NUMBER, "1"),
            Token(RatTokens.SEMICOLON),
            Token(RatTokens.IDENT, "fn"),
            Token(RatTokens.LBRACE),
            Token(RatTokens.IDENT, "a"),
            Token(RatTokens.ASSIGN),
            Token(RatTokens.NUMBER, "42"),
            Token(RatTokens.SEMICOLON),
            Token(RatTokens.IDENT, "@v"),
            Token(RatTokens.ASSIGN),
            Token(RatTokens.IDENT, "alloc"),
            Token(RatTokens.LPAREN),
            Token(RatTokens.RPAREN),
            Token(RatTokens.SEMICOLON),
            Token(RatTokens.RBRACE),
        ],
        default_token_tree=rat_tree,
    )
