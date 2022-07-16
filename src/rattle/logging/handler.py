import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .message import Event
from .levels import Level


class Destination(ABC):
    @abstractmethod
    def send_message(self, m: str) -> None:
        pass


class Formatter(ABC):
    @abstractmethod
    def format_message(self, m: Event) -> str:
        pass


@dataclass
class Handler:
    level: int
    destination: Destination
    formatter: Formatter

    def can_handle(self, msg: Event) -> bool:
        if msg.level.value >= self.level.value:
            return True

        return False

    @classmethod
    def from_destination_and_formatter(cls, destination, formatter, level=Level.WARN_LATER):
        return cls(level, destination, formatter)


class JSONFormatter(Formatter):
    def format_message(self, m: Event) -> str:
        return json.dumps(
            {
                "action": m.action,
                "timestamp": m.timestamp.timestamp(),
                "action_state": m.state,
                "attrs": json.dumps(m.fields),
            }
        )


class HumanReadableFormatter(Formatter):
    def format_message(self, m: Event) -> str:
        kvps = ", ".join(f"{k}={v!r}" for k, v in m.fields.items())
        return f"{m.level.name} [{m.timestamp}] ({m.source_logger.name}) |{m.action.name}| {m.name}: {kvps}"


class FileLineWriterDestination(Destination):
    def __init__(self, fileobj):
        self.fileobj = fileobj

    def send_message(self, m: str) -> None:
        self.fileobj.write(m + "\n")
