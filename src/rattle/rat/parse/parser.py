import sys
import ast

from enum import (
    Enum,
    auto,
)

from rattle.rat.parse import (
    tokens,
)
from rattle.rat import (
    ast as rast,
)


class TokenType(Enum):
    # symbols
    ASSIGN = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    DOT = auto()
    IDENTIFIER = auto()
    NUMBER = auto()


class RatParser(Parser):
    def parse_program(
        self,
    ):
        pass


def parse(
    src: src,
) -> rast.RatAST:
    pass
