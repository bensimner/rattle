from dataclasses import (
    dataclass,
)

from rattle.utils.enums import (
    enum,
    auto,
)


# sentinel to mean "skip this token" in the output AST
SKIP = object()

# sentinel meaning "tree tokenized correctly, but continue with 'next'"
CONTINUE = object()


@enum
class TokenType:
    IDENT = auto()
    STRING = auto()
    NUMBER = auto()

    def __format__(self, fmt):
        if fmt == "src":
            if self == TokenType.STRING:
                return f'"{self.value}"'
            elif self == TokenType.NUMBER:
                return f"{self.value}"
            elif self == TokenType.IDENT:
                return f"{self.value}"
            else:
                return f'"{self.value}"'
        return super().__format__(fmt)


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
