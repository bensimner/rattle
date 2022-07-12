""" rattle.api contains the runtime components of the rattle library
"""

from rattle.api import (
    _checker,
)
from rattle.api import (
    _stub,
)

R = _checker.RuntimeChecker()
Rstub = _stub.RuntimeChecker()
