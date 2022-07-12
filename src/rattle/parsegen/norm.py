from rattle.parsegen import (
    visitor,
)
from rattle.parsegen.token_info import (
    Token,
    TokenType,
)


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
            # check whether this is the name of a token
            if self.grammar.tokens is not None:
                tokens = self.grammar.tokens
            else:
                tokens = TokenType

            if tokens.has_member(atom.value):
                atom.value = Token(tokens.get(atom.value))
