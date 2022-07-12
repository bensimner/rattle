from rattle import (
    errors,
)
from rattle.utils.indexed_stream import (
    IndexedStream,
)
from rattle.logging import (
    log_action,
)


class Parser:
    def __init__(self, stream):
        self.stream = IndexedStream(stream)
        self._i = 0
        self._lookahead = None

    def at_eof(
        self,
    ):
        try:
            # tokens left?
            self.peek()
        except IndexError:
            return True
        else:
            return False

    def checkpoint(
        self,
    ):
        return self._i

    def restore(self, chkp):
        self._i = chkp

    def peek(self):
        return self.stream[self._i]

    def consume(
        self,
    ):
        self._i += 1

    def accept(self, tok):
        with log_action(
            "accept",
            token=repr(tok),
        ) as ctx:
            try:
                lk = self.peek()
            except IndexError:
                raise errors.RatParseError.with_pos(
                    self,
                    "Unexpected end of stream",
                )

            if lk.token_type != tok.token_type:
                raise errors.RatParseError.with_pos(
                    self,
                    f"Expected {tok} but got {lk}",
                )

            if tok.value is not None and lk.value != tok.value:
                raise errors.RatParseError.with_pos(
                    self,
                    f"Expected {tok.value} but got {lk.value}",
                )

            self.consume()
            ctx.add_success_fields(consumed=repr(lk))
            return lk
