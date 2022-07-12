import sys
import types
import inspect
import operator
import itertools
from functools import (
    wraps,
    cached_property,
)

from rattle.api import (
    ghost,
)
from rattle.utils.operators import (
    chain,
    lor,
    land,
)


def asserter(
    typ,
    assertion_func,
    args,
    kwargs,
    invert=True,
    decorated_func=None,
):
    if not isinstance(
        assertion_func,
        types.FunctionType,
    ):
        raise ValueError(f"{typ} expects function not {type(assertion_func)}")

    try:
        b = assertion_func(
            *args,
            **kwargs,
        )
        if invert:
            b = not b
        assert b
    except AssertionError:
        src = inspect.getsource(assertion_func)
        if decorated_func is not None:
            sys.stderr.write(f"Failed @{typ} on {decorated_func}:\n")
            self = args[0]
            ghost_st = self.ghost
            sys.stderr.write(f" obj={self}\n")
            sys.stderr.write(f" obj.ghost={ghost_st}\n")
        else:
            sys.stderr.write(f"Failed {typ}:\n")
        sys.stderr.write(f" check={assertion_func}{src}\n")
        sys.stderr.write(f" {args=}\n")
        sys.stderr.write(f" {kwargs=}\n")
        raise


def decorate_with_runners(
    func,
):
    runners = func.__rattle_checks__

    @wraps(func)
    def wrapper(
        *args,
        **kwargs,
    ):
        self = args[0]
        it = iter(runners)

        def update_ghost(
            attrs,
            maybe_include_ret=False,
        ):
            for (
                var,
                f,
            ) in attrs.items():
                kws = dict(kwargs)
                if maybe_include_ret:
                    if "ret" in inspect.signature(f).parameters:
                        kws["ret"] = ret
                self.ghost[var] = f(
                    *args,
                    **kws,
                )

        for (
            typ,
            r,
        ) in it:
            if typ in (
                "ensures",
                "reject",
            ):
                break

            if typ == "requires":
                if r is not None:
                    asserter(
                        typ,
                        r,
                        args,
                        kwargs,
                    )
            elif typ == "ghost":
                update_ghost(r)

        pre = self.ghost.clone()
        ret = func(
            *args,
            **kwargs,
        )
        self.ghost.pre = pre

        # got to "ensures" or not?
        if typ is not None and typ in (
            "ensures",
            "reject",
        ):
            for (typ, r,) in itertools.chain(
                [
                    (
                        typ,
                        r,
                    )
                ],
                it,
            ):
                if typ == "ensures":
                    if r is not None:
                        kws = dict(kwargs)
                        if "ret" in inspect.signature(r).parameters:
                            kws["ret"] = ret
                        asserter(
                            typ,
                            r,
                            args,
                            kws,
                        )
                elif typ == "ghost":
                    update_ghost(
                        r,
                        maybe_include_ret=True,
                    )
                elif typ == "reject":
                    if r is not None:
                        kws = dict(kwargs)
                        if "ret" in inspect.signature(r).parameters:
                            kws["ret"] = ret
                        asserter(
                            typ,
                            r,
                            args,
                            kws,
                            invert=True,
                        )
                else:
                    raise ValueError("Cannot @requires after @ensures")

        return ret

    return wrapper


def _add_check(typ):
    def f(
        self,
        assertion_func=None,
    ):
        def deco(f):
            if not hasattr(
                f,
                "__rattle_checks__",
            ):
                f.__rattle_checks__ = []

            f.__rattle_checks__.append(
                (
                    typ,
                    assertion_func,
                )
            )
            return f

        return deco

    f.__name__ == typ
    return f


class RuntimeChecker:
    def ensure(
        self,
        assertion_func,
    ):
        asserter(
            "ensure",
            assertion_func,
            (),
            {},
        )

    def require(
        self,
        assertion_func,
    ):
        asserter(
            "require",
            assertion_func,
            (),
            {},
        )

    def reject(
        self,
        assertion_func,
    ):
        asserter(
            "require",
            assertion_func,
            (),
            {},
            invert=True,
        )

    requires = _add_check("requires")
    ensures = _add_check("ensures")
    rejects = _add_check("rejects")

    def check(self, cls):
        for (
            name,
            attr,
        ) in vars(cls).items():
            if hasattr(
                attr,
                "__rattle_checks__",
            ):
                attr.__rattle_checks__.reverse()
                setattr(
                    cls,
                    name,
                    decorate_with_runners(attr),
                )

        ghost_attrs = []
        for (
            name,
            attr,
        ) in vars(cls).items():
            if name.startswith("ghost_"):
                if not isinstance(
                    attr,
                    ghost.GhostAttr,
                ):
                    raise ValueError("ghost_* attributes must be ghost.attr()s")
                ghost_attrs.append(attr)
        cls.ghost = ghost.GhostData(ghost_attrs=ghost_attrs)

        return cls

    @cached_property
    def ghost(self):
        return ghost.Ghost()
