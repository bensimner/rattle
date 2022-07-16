from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from inspect import signature
import datetime as dt
import typing
from contextvars import ContextVar
import uuid

from rattle.utils.enums import enum, auto

if typing.TYPE_CHECKING:
    from .logger import Logger

from .levels import Level
from .message import Event


@enum
class ActionState:
    STARTED = auto()
    ERROR = auto()
    STOP = auto()


@dataclass
class Action:
    source_logger: "Logger"
    task: "Task"  # all Actions have an associated task
    name: str
    level: Level
    state: ActionState
    fields: dict[str, object]
    uuid: int = field(default_factory=uuid.uuid4)
    error_fields: dict[str, object] = field(default_factory=dict)
    success_fields: dict[str, object] = field(default_factory=dict)

    def add_fields(self, **new_fields):
        self.fields.update(new_fields)

    add_field = add_fields

    def add_error_fields(self, **err_fields):
        self.error_fields.update(err_fields)

    add_error_field = add_error_fields

    def add_success_fields(self, **err_fields):
        self.success_fields.update(err_fields)

    add_success_field = add_success_fields

    def add_message(self, name, *, level=None, **fields) -> None:
        if level is None:
            level = self.level

        msg = Event(self.source_logger, dt.datetime.now(), self, level, name, fields)
        self.source_logger.log_message(msg)


@dataclass
class Task:
    current_actions: list[Action] = field(default_factory=list)
    uuid: int = field(default_factory=uuid.uuid4)


current_task = ContextVar("rattle.current_task", default=None)


class ActionProducer:
    """A Logger mixin that gives it the ability to produce Actions"""

    @contextmanager
    def start(self, name, level: int = Level.IN_TESTS, **fields):
        # when we start a new action,
        # attach it to the current Task
        task = current_task.get()
        if task is None:
            task = Task()
            current_task.set(task)

        ctx = Action(self, task, name, level, ActionState.STARTED, fields)
        task.current_actions.append(ctx)
        ctx.add_message("started", **ctx.fields)

        try:
            yield ctx
        except:
            ctx.state = ActionState.ERROR
            ctx.add_message("error", **ctx.fields, **ctx.error_fields)
            task.current_actions.pop()
            raise
        else:
            ctx.state = ActionState.STOP
            ctx.add_message("stop", **ctx.fields, **ctx.success_fields)
            task.current_actions.pop()


class FunctionCallLogger:
    """A Logger mixin that gives it the ability to log methods and functions"""

    def log_calls(self, func=None, skip_args=(), include_attrs=(), include_ctx=False, include_return=True):
        def deco(f):
            sig = signature(f)

            @wraps(f)
            def wrapper(*args, **kwargs):
                if include_ctx:
                    kwargs["ctx"] = None  # placeholder

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

                with self.start(f.__name__, **keys) as ctx:
                    if include_ctx:
                        kwargs["ctx"] = ctx

                    v = f(*args, **kwargs)

                    if include_return:
                        ctx.add_field(returns=v)

                    return v

            return wrapper

        if func is not None:
            return deco(func)
        else:
            return deco
