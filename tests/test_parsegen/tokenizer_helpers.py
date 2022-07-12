import io

from rattle.parsegen.grammar import Grammar
from rattle.parsegen.tokenizer import tokenize, default_tree
from rattle.parsegen.token_info import Token


def assert_tokenizes_to(
    gram: Grammar | None, src: str, expected_tokens: list[Token], default_token_tree=default_tree
) -> None:
    if gram is not None:
        token_tree = gram.token_tree
    else:
        token_tree = default_token_tree
    toks = list(tokenize(io.StringIO(src), filename="<unknown>", token_tree=token_tree))

    for actual, expected in zip(toks, expected_tokens):
        assert actual.token_type == expected.token_type

        if expected.value is not None:
            assert expected.value == actual.value

    assert len(toks) == len(expected_tokens)


class TokenEnumEq:
    """Helper for equality over rattle.utils.enums types"""

    def __init__(self, tokens):
        self.tokens = tokens

    def __eq__(self, other_enum):
        """for TokenEnumEq(...) == SomeEnum

        check that they have the same tokens with the same values
        """

        this_keys = set(name for name, _ in self.tokens)
        others = {m.name: m.value for m in other_enum.members()}

        # they have different keys
        if this_keys.symmetric_difference(set(others)) != set():
            return False

        for k, v in self.tokens:
            # (at least) one of the values isn't the same
            if v != others[k]:
                return False

        # all good!
        return True
