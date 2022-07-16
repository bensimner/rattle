from dataclasses import dataclass, field
from contextlib import contextmanager

from .cache import loggers
from .handler import Handler
from .levels import Level
from .config import LoggerConfiguration
from .actions import ActionProducer, FunctionCallLogger
from .message import Event


def get_logger(name: str) -> "Logger":
    return Logger.from_name(name)


@dataclass
class Logger(ActionProducer, FunctionCallLogger):
    # the name of the logger
    name: str

    # configuration
    config: LoggerConfiguration = field(default_factory=LoggerConfiguration)

    # loggers are hierarchical
    children: list["Logger"] = field(default_factory=list)
    parent: "Logger | None" = None

    level = Level

    def log_message(self, msg: Event) -> None:
        """Low-level API for sending messages directly to registered handlers"""
        for logger in self.ancestors():
            for handler in logger.config.handlers:
                if handler.can_handle(msg):
                    s = handler.formatter.format_message(msg)
                    handler.destination.send_message(s)

    def ancestors(self):
        """yield this logger, and the parent hierarchy up to and including the root logger"""
        yield self
        if self.parent:
            yield from self.parent.ancestors()

    @classmethod
    def from_name(cls, name: str):
        if name in loggers:
            return loggers[name]

        parent = root_logger

        up_to = None
        for part in name.split("."):
            if up_to is None:
                up_to = part
            else:
                up_to += "." + part

            if up_to in loggers:
                logger = loggers[up_to]
            else:
                logger = cls(name)
                loggers[name] = logger
                logger.parent = parent
                parent.children.append(logger)
            parent = logger
        return logger


# make a root logger
root_logger = Logger("root")
