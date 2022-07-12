from itertools import (
    count,
)


def enum(cls):
    """make a class an enum

    >>> @enum
    ... class Foo:
    ...     x = 1
    ...     y = 2
    >>> Foo.x
    <Foo.x: 1>
    >>> Foo.y
    <Foo.y: 2>
    >>> Foo["x"]
    <Foo.x: 1>
    >>> Foo.x.name
    x
    >>> Foo.x.value
    1
    >>> @enum
    ... class Bar(Foo):
    ...   z = 3
    >>> list(Bar.members())  # Bar's members are first
    [<Bar.z: 3>, <Foo.x: 1>, <Foo.y: 1>]
    >>> "x" in Bar
    True
    >>> "z" in Foo
    False
    """

    classattrs = [
        (k, v)
        for (
            k,
            v,
        ) in vars(cls).items()
        if not k.startswith("_")
    ]

    def new_init(
        self,
        name,
        value,
    ):
        self.name = name
        self.value = value

    cls.__init__ = new_init

    def new_repr(
        self,
    ):
        return f"<{self.__class__.__name__}.{self.name}: {self.value!r}>"

    cls.__repr__ = new_repr

    enum_members = {}
    for (
        name,
        value,
    ) in classattrs:
        v = cls(
            name,
            value,
        )
        setattr(
            cls,
            name,
            v,
        )
        enum_members[name] = v

    cls.__enum_members__ = enum_members

    @classmethod
    def cls_getitem(kls, k):
        return kls.__enum_members__[k]

    cls.get = cls_getitem

    @classmethod
    def members(
        kls,
    ):
        for m in kls.__mro__:
            if hasattr(
                m,
                "__enum_members__",
            ):
                yield from m.__enum_members__.values()

    cls.members = members

    @classmethod
    def contains(kls, key):
        for m in kls.__mro__:
            if hasattr(
                m,
                "__enum_members__",
            ):
                if key in m.__enum_members__:
                    return True
        return False

    cls.has_member = contains
    return cls


_counter = count()


def auto():
    """an auto-incrementing integer, for use in an @enum"""
    return next(_counter)


def _make_enum_member(cls, name, value):
    new_value = cls(name, value)
    return new_value
