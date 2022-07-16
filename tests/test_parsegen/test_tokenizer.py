from textwrap import dedent

from rattle.parsegen.token_info import TokenType, Token
from rattle.parsegen.tokenizer import default_tree
from rattle.parsegen.metagram import MetaGram

from .tokenizer_helpers import assert_tokenizes_to


def test_tokenize_empty():
    assert_tokenizes_to(None, "", [])


def test_tokenize_single_identifier():
    assert_tokenizes_to(None, "a", [Token(TokenType.IDENT, "a")])


def test_tokenize_single_identifier_multichar():
    assert_tokenizes_to(None, "aa", [Token(TokenType.IDENT, "aa")])


def test_tokenize_two_identifiers():
    assert_tokenizes_to(None, "aa bb", [Token(TokenType.IDENT, "aa"), Token(TokenType.IDENT, "bb")])


def test_tokenize_string():
    assert_tokenizes_to(None, '"ab"', [Token(TokenType.STRING, '"ab"')])


def test_tokenize_multilinestring():
    assert_tokenizes_to(None, '"a\nb"', [Token(TokenType.STRING, '"a\nb"')])


def test_tokenize_digit():
    assert_tokenizes_to(None, "4", [Token(TokenType.NUMBER, "4")])


def test_tokenize_number():
    assert_tokenizes_to(None, "42", [Token(TokenType.NUMBER, "42")])


def test_tokenize_comment():
    assert_tokenizes_to(None, "#foo", [])


def test_tokenize_small_prog():
    prog = dedent(
        """\
        a b#c d#
        #
         #"ax"
        "a x" 12#
        cd"x"
        a14
    """
    )
    tokens = [
        Token(TokenType.IDENT, "a"),
        Token(TokenType.IDENT, "b"),
        Token(TokenType.STRING, '"a x"'),
        Token(TokenType.NUMBER, "12"),
        Token(TokenType.IDENT, "cd"),
        Token(TokenType.STRING, '"x"'),
        Token(TokenType.IDENT, "a14"),
    ]
    assert_tokenizes_to(None, prog, tokens)
