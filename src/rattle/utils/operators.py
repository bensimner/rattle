import types
import attrs

import operator


@attrs.define
class Operator:
    name: str
    desc: str
    methname: str
    op: types.FunctionType
    nargs: int


def chain(
    op,
    lhs,
    rhs,
    *rest,
):
    """chains `op` over a sequence of operations [lhs, rhs, *rest] like Python would

    chain(op, a, b, c) == op(a, b) and op(b, c)
    """
    r = op(lhs, rhs)

    lhs = rhs
    for rhs in rest:
        r = r and op(
            lhs,
            rhs,
        )
        lhs = rhs

    return r


def land(a, b, /):
    """equivalent to `a and b`"""
    return a and b


def lor(a, b, /):
    """equivalent to `a or b`"""
    return a or b


OPERATORS = [
    Operator(
        "Addition",
        "a + b",
        "__add__",
        operator.add,
        2,
    ),
    Operator(
        "Concatenation",
        "seq1 + seq2",
        "concat",
        operator.concat,
        2,
    ),
    Operator(
        "Containment Test",
        "obj in seq",
        "__contains__",
        operator.contains,
        2,
    ),
    Operator(
        "Division",
        "a / b",
        "__truediv__",
        operator.truediv,
        2,
    ),
    Operator(
        "Division",
        "a // b",
        "__floordiv__",
        operator.floordiv,
        2,
    ),
    Operator(
        "Bitwise And",
        "a & b",
        "__and__",
        operator.and_,
        2,
    ),
    Operator(
        "Bitwise Exclusive Or",
        "a ^ b",
        "__xor__",
        operator.xor,
        2,
    ),
    Operator(
        "Bitwise Inversion",
        "~ a",
        "__invert__",
        operator.invert,
        1,
    ),
    Operator(
        "Bitwise Or",
        "a | b",
        "__or__",
        operator.or_,
        2,
    ),
    Operator(
        "Exponentiation",
        "a ** b",
        "__pow__",
        operator.pow,
        2,
    ),
    Operator(
        "Identity",
        "a is b",
        "is_",
        operator.is_,
        2,
    ),
    Operator(
        "Negated Identity",
        "a is not b",
        "is_not",
        operator.is_not,
        2,
    ),
    Operator(
        "Indexed Assignment",
        "obj[k] = v",
        "__setitem__",
        operator.setitem,
        2,
    ),
    Operator(
        "Indexed Deletion",
        "del obj[k]",
        "__delitem__",
        operator.delitem,
        2,
    ),
    Operator(
        "Indexing",
        "obj[k]",
        "__getitem__",
        operator.getitem,
        2,
    ),
    Operator(
        "Left Shift",
        "a << b",
        "__lshift__",
        operator.lshift,
        2,
    ),
    Operator(
        "Modulo",
        "a % b",
        "__mod__",
        operator.mod,
        2,
    ),
    Operator(
        "Multiplication",
        "a * b",
        "__mul__",
        operator.mul,
        2,
    ),
    Operator(
        "Matrix Multiplication",
        "a @ b",
        "__matmul__",
        operator.matmul,
        2,
    ),
    Operator(
        "Negation (Arithmetic)",
        "- a",
        "__neg__",
        operator.neg,
        1,
    ),
    Operator(
        "Positive",
        "+ a",
        "__pos__",
        operator.pos,
        1,
    ),
    Operator(
        "Right Shift",
        "a >> b",
        "__rshift__",
        operator.rshift,
        2,
    ),
    Operator(
        "Subtraction",
        "a - b",
        "__sub__",
        operator.sub,
        2,
    ),
    Operator(
        "Ordering",
        "a < b",
        "__lt__",
        operator.lt,
        2,
    ),
    Operator(
        "Ordering",
        "a <= b",
        "__le__",
        operator.le,
        2,
    ),
    Operator(
        "Equality",
        "a == b",
        "__eq__",
        operator.eq,
        2,
    ),
    Operator(
        "Difference",
        "a != b",
        "__ne__",
        operator.ne,
        2,
    ),
    Operator(
        "Ordering",
        "a >= b",
        "__ge__",
        operator.ge,
        2,
    ),
    Operator(
        "Ordering",
        "a > b",
        "__gt__",
        operator.gt,
        2,
    ),
    Operator(
        "Get Attribute",
        "x.y",
        "__getattr__",
        getattr,
        2,
    ),
]
