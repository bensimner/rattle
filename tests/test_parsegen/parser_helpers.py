import io

import pytest

from rattle import errors
from rattle.parsegen.grammar import Grammar, GrammarExp
from rattle.parsegen.tokenizer import tokenize
from rattle.parsegen.token_info import Token


def assert_parses(gram: Grammar, src: str) -> None:
    f = io.StringIO(src)
    gram.parse(f)
    assert True


def assert_not_parses(gram: Grammar, src: str) -> None:
    f = io.StringIO(src)  #
    with pytest.raises(errors.RatParseError, match="Unexpected EOF"):
        gram.parse(f)


def assert_parses_to(gram: Grammar, src: str, expected_ast: GrammarExp) -> None:
    f = io.StringIO(src)
    ast = gram.parse(f)
    assert ast == expected_ast
