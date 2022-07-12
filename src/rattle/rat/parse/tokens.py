from rattle.parsegen import (
    token_info,
)
from rattle.parsegen import (
    tokenizer,
)

from rattle.utils.enums import (
    enum,
    auto,
)


@enum
class RatTokens(token_info.TokenType):
    ASSIGN = ":="
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    DOT = "."
    SEMICOLON = ";"


rat_tree = tokenizer.build_prefix_tree(RatTokens)
