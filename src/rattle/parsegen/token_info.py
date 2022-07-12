from dataclasses import (
    dataclass,
)

from rattle.utils.enums import (
    enum,
    auto,
)


@enum
class TokenType:
    IDENT = auto()
    STRING = auto()
    NUMBER = auto()


Lineno = int
Column = int


@dataclass
class SourceInfo:
    file: str
    start: tuple[
        Lineno,
        Column,
    ]
    stop: tuple[
        Lineno,
        Column,
    ]


@dataclass
class Token:
    token_type: TokenType
    value: str | None = None
    source_info: SourceInfo | None = None

    @property
    def string_value(
        self,
    ):
        if self.token_type != TokenType.STRING:
            raise ValueError(f"Can only get the .string_value of a STRING, not a {self.token_type}")

        return self.value[1:-1]  # skip quote marks, which are embedded in the token
