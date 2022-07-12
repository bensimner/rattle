from rattle.parsegen.token_info import TokenType, Token
from rattle.parsegen.tokenizer import default_tree
from rattle.parsegen.metagram import MetaGram

from .tokenizer_helpers import assert_tokenizes_to


def test_tokenize_single_identifier():
    assert_tokenizes_to(None, "a", [Token(TokenType.IDENT, "a")])


def test_tokenize_single_identifier_multichar():
    assert_tokenizes_to(None, "aa", [Token(TokenType.IDENT, "aa")])


def test_tokenize_two_identifiers():
    assert_tokenizes_to(None, "aa bb", [Token(TokenType.IDENT, "aa"), Token(TokenType.IDENT, "bb")])
