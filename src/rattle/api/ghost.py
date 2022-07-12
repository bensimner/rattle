from functools import (
    wraps,
)
from copy import (
    deepcopy,
)
import types

import attrs


@attrs.define
class InstanceGhostData:
    ghost_data: dict = None
    pre: "InstanceGhostData" = None

    def __getattr__(self, attr):
        return self.ghost_data[attr]

    def __getitem__(self, k):
        return self.ghost_data[k]

    def __setitem__(self, k, v):
        self.ghost_data[k] = v

    def __call__(
        self,
        *args,
        **vars,
    ):
        if len(args) == 1:
            [name] = args
            if vars != {}:
                raise ValueError("can only get or set ghost values, not both")
            return self.ghost_data[name]
        elif len(args) == 2:
            (
                args,
                kwargs,
            ) = args
        elif len(args) == 0:
            (args, kwargs,) = (
                (),
                {},
            )
        else:
            raise ValueError("Invalid ghost() call")

        self.ghost_data.update(
            {
                n: v(
                    *args,
                    **kwargs,
                )
                for (
                    n,
                    v,
                ) in vars.items()
            }
        )

    def clone(self):
        return InstanceGhostData(ghost_data=deepcopy(self.ghost_data))


@attrs.define
class GhostData:
    ghost_attrs: list

    def __get__(
        self,
        instance,
        owner=None,
    ):
        if instance is not None:
            if "ghost" not in instance.__dict__:
                data = {}
                for attr in self.ghost_attrs:
                    data[attr.name] = attr.default()
                instance.__dict__["ghost"] = InstanceGhostData(
                    ghost_data=data,
                    pre={},
                )
            return instance.__dict__["ghost"]
        return self


@attrs.define
class GhostAttr:
    name: str = None
    default_factory: types.FunctionType = None

    def __set_name__(
        self,
        owner,
        name,
    ):
        if not name.startswith("ghost_"):
            raise ValueError("ghost attributes must start with 'ghost_'")
        self.name = name[len("ghost_") :]

    def default(
        self,
    ):
        if self.default_factory is not None:
            return self.default_factory()
        else:
            return None


class Ghost:
    def __call__(
        self,
        arg=None,
        /,
        **attrs,
    ):
        if arg is not None:
            return arg

        def deco(f):
            if not hasattr(
                f,
                "__rattle_checks__",
            ):
                f.__rattle_checks__ = []

            f.__rattle_checks__.append(
                (
                    "ghost",
                    attrs,
                )
            )
            return f

        return deco

    def attr(
        self,
        /,
        default_factory=None,
    ):
        return GhostAttr(default_factory=default_factory)
