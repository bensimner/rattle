from dataclasses import dataclass, field
import datetime as dt
import typing


if typing.TYPE_CHECKING:
    from .logger import Logger
    from .levels import Level
    from .actions import Action


@dataclass
class Event:
    """A single Event message"""

    source_logger: "Logger"
    timestamp: dt.datetime
    action: "Action"
    level: "Level"
    name: str
    fields: dict[str, object]
