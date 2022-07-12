class RattleError(Exception):
    pass


class RatParseError(RattleError):
    """An error during parsing Rat"""

    @classmethod
    def with_pos(
        cls,
        parser,
        msg,
    ):
        try:
            lk = parser.peek()
            return cls(f"Error on {lk.value} at {lk.source_info}: {msg}")
        except IndexError:
            return cls("Unexpected end of stream")


class TokenizeError(RattleError):
    """An error during tokenization"""
