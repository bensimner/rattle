from functools import (
    wraps,
)

import attrs

import rattle.utils.operators as rattle_ops


def identity(v):
    return v


@attrs.define
class Sym:
    op: rattle_ops.Operator
    data: list

    def force(self):
        data = [
            d.force()
            if isinstance(
                d,
                Sym,
            )
            else d
            for d in self.data
        ]
        return self.op.op(*data)

    def __bool__(
        self,
    ):
        raise ValueError("Cannot use symbolic variable in boolean context, use one of .logical_{and,or,truth}")

    def __len__(
        self,
    ):
        raise ValueError("Cannot use len() on symbolic variable, use .len()")


def _attach_operator(klass, op):
    @wraps(op.op)
    def meth(*args):
        if len(args) != op.nargs:
            raise TypeError(f"{op.name} expected {op.nargs} arguments, but got {len(args)}")

        return Sym(op, args)

    setattr(
        klass,
        op.methname,
        meth,
    )


for op in rattle_ops.OPERATORS:
    _attach_operator(Sym, op)

extra_ops = [
    rattle_ops.Operator(
        "Logical And",
        "a and b",
        "logical_and",
        rattle_ops.land,
        2,
    ),
    rattle_ops.Operator(
        "Logical Or",
        "a or b",
        "logical_or",
        rattle_ops.lor,
        2,
    ),
    rattle_ops.Operator(
        "Logical Not",
        "not a",
        "logical_not",
        rattle_ops.operator.not_,
        1,
    ),
    rattle_ops.Operator(
        "Logical Truth",
        "bool(obj)",
        "logical_truth",
        rattle_ops.operator.truth,
        1,
    ),
    rattle_ops.Operator(
        "Local variable",
        "x",
        "local",
        identity,
        1,
    ),
    rattle_ops.Operator(
        "Length",
        "len(a)",
        "len",
        len,
        1,
    ),
]

for op in extra_ops:
    _attach_operator(Sym, op)
