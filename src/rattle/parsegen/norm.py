from rattle.parsegen import (
    visitor,
)
from rattle.parsegen.token_info import (
    Token,
    TokenType,
)

from rattle.utils.itertools import find_exactly_one


class GrammarNormalizer(visitor.GrammarWalker):
    def __init__(
        self,
        grammar,
    ):
        self.grammar = grammar

    def visit_Atom(self, atom):
        if isinstance(
            atom.value,
            str,
        ):
            if self.grammar.tokens is not None:
                tokens = self.grammar.tokens
            else:
                tokens = TokenType

            # check whether this is the name of a token
            if tokens.has_member(atom.value):
                atom.value = Token(tokens.get(atom.value))

            # check if this is a value of a token
            try:
                x = find_exactly_one(t for t in tokens.members() if t.value == atom.value)
                atom.value = Token(tokens.get(x.name))
            except ValueError:
                pass
