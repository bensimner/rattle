""" rattle.logging

a wrapper around eliot with a slightly nicer API
"""

from functools import (
    wraps,
)
from contextlib import (
    contextmanager,
)
from inspect import (
    signature,
)

import eliot
import eliot.json

ELIOT_DESTINATION = None


@contextmanager
def log_action(action_type: str, **fields):
    with eliot.start_action(action_type=action_type, **fields) as ctx:
        yield ctx


def log_call(func=None, *, include_ctx=True, include_return=True, skip_args=(), include_attrs=()):
    def deco(func):
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bargs = sig.bind(*args, **kwargs)
            _args = bargs.arguments

            for a in skip_args:
                del _args[a]

            keys = {}

            if _args:
                keys["args"] = _args

            if include_attrs:
                attrs = {}
                for a in include_attrs:
                    attrs[a] = getattr(
                        args[0],
                        a,
                    )
                keys["attrs"] = attrs

            if include_ctx:
                kwargs["ctx"] = ctx

            with log_action(func.__name__, **keys) as ctx:
                v = func(*args, **kwargs)

                if include_return:
                    ctx.add_success_fields(returns=repr(v))

                return v

        return wrapper

    if func is None:
        return deco
    else:
        return deco(func)


def enable():
    global ELIOT_DESTINATION
    ELIOT_DESTINATION = eliot.FileDestination(
        open(
            "rattle.log",
            "wb",
        ),
        encoder=eliot.json.EliotJSONEncoder,
    )
    eliot.add_destinations(ELIOT_DESTINATION)


def disable():
    eliot.remove_destination(ELIOT_DESTINATION)
