from dataclasses import (
    dataclass,
)

from rattle.rat.parse.tokens import (
    TokenInfo,
)


@dataclass
class RatAST:
    source_tokens: list[object]  # this source info may come from either Rat or Python


@dataclass
class Literal(RatAST):
    # since we're embedding into Python we can just use Python objects
    value: object


@dataclass
class Identifier(RatAST):
    ident: str


@dataclass
class Assign(RatAST):
    name: Identifier
    value: RatAST


@dataclass
class FuncDefn(RatAST):
    params: list[Identifier]
    body: RatAST


@dataclass
class Call(RatAST):
    func: RatAST
    args: list[RatAST]
