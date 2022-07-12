import io

from rattle.parsegen.token_info import TokenType
from rattle.parsegen.tokenizer import tokenize, default_tree


def test_match_ident():
    (tok_src, tok_type), rem = default_tree.split_prefix("aa")
    assert tok_type == TokenType.IDENT
    assert tok_src == "aa"
    assert rem == ""


def test_match_two_idents():
    (tok_src, tok_type), rem = default_tree.split_prefix("aa bb")
    assert tok_type == TokenType.IDENT
    assert tok_src == "aa"
    assert rem == " bb"

    (tok_src, tok_type), rem = default_tree.split_prefix(rem)
    assert tok_type is None
    assert tok_src == ""
    assert rem == " bb"

    (tok_src, tok_type), rem = default_tree.split_prefix(rem[1:])
    assert tok_type == TokenType.IDENT
    assert tok_src == "bb"
    assert rem == ""
