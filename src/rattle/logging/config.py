import sys
from dataclasses import dataclass, field

from . import levels, handler, logger


@dataclass
class LoggerConfiguration:
    handlers: list["handler.Handler"] = field(default_factory=list)


def basic_config(*, root=None, level=None):
    """Configures the root logger with a default handler that prints warnings to stderr"""

    if root is None:
        root = logger.root_logger

    default_destination = handler.FileLineWriterDestination(sys.stderr)
    default_formatter = handler.HumanReadableFormatter()
    default_handler = handler.Handler.from_destination_and_formatter(
        default_destination, default_formatter, level=level
    )
    root.config.handlers.append(default_handler)
