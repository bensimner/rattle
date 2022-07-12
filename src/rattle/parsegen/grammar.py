from dataclasses import (
    dataclass,
    field,
)
from functools import (
    partial,
)
from xml.etree.ElementInclude import (
    include,
)

from rattle import (
    errors,
)
from rattle.utils.enums import (
    enum,
    auto,
)
from rattle.logging import (
    log_action,
    log_call,
)

from rattle.parsegen import (
    token_info,
)
from rattle.parsegen.tokenizer import (
    tokenize,
    build_prefix_tree,
    default_tree,
)
from rattle.parsegen.parser import (
    Parser,
)
from rattle.parsegen import (
    norm,
)


@dataclass(kw_only=True)
class Grammar:
    tokens: object = None
    header: str | None = None
    rules: "dict[str, Rule]" = None
    start_symbol: str = None
    _cached_token_tree: object | None = field(
        default=None,
        init=False,
        repr=False,
    )

    @property
    def token_tree(
        self,
    ):
        if self._cached_token_tree is None:
            if self.tokens is None:
                self._cached_token_tree = default_tree
            else:
                self._cached_token_tree = build_prefix_tree(self.tokens)
        return self._cached_token_tree

    def parse(
        self,
        f,
        filename: str = "<unknown>",
    ):
        # produce token stream
        toks = tokenize(
            f,
            filename=filename,
            token_tree=self.token_tree,
        )
        parser = Parser(toks)

        # run the parser for the given start symbol
        val = self[self.start_symbol](parser)

        # check consumed entire input
        if not parser.at_eof():
            raise errors.RatParseError("Unexpected EOF")

        return val

    def __getitem__(
        self,
        parser_name,
    ):
        rule = self.rules[parser_name]
        return partial(
            rule.parse,
            self,
        )

    def __getattr__(self, attr):
        if attr.startswith("parse_"):
            name = attr.removeprefix("parse_")
            return self[name]
        else:
            return super().__getattr__(attr)

    @classmethod
    def from_header_and_rules(
        cls,
        hds,
        rules,
    ):
        headers = {
            k: v
            for hd in hds
            for (
                k,
                v,
            ) in hd.items()
        }
        return cls(
            **headers,
            rules=rules,
        )

    def normalize(
        self,
    ):
        """normalize this grammar and return itself"""
        norm.GrammarNormalizer(self).visit(self)
        return self


def grammar(cls):
    tokens = None
    header = None
    start_symbol = None
    rules = {}

    # collect vars() of cls and combine them
    ks = []
    for (
        k,
        v,
    ) in vars(cls).items():
        if k == "header":
            header = v
        elif k == "start_symbol":
            start_symbol = v
        elif k == "Tokens":
            tokens = v
        elif isinstance(v, Rhs):
            rules[k] = Rule(k, v)
        elif isinstance(
            v,
            GrammarExp,
        ):
            raise ValueError(
                f"""@grammar '{cls.__name__}' should have Rhs top-level rule for {k!r} not {type(v)}
(Did you want to use .as_rhs()?"""
            )
        else:
            continue

        ks.append(k)

    if start_symbol is None:
        raise ValueError("@grammar must have a 'start_symbol'")

    if tokens is None:
        tokens = token_info.TokenType

    return Grammar(
        tokens=tokens,
        header=header,
        rules=rules,
        start_symbol=start_symbol,
    )


class GrammarExp:
    pass


@dataclass
class Rule(GrammarExp):
    lhs: str
    rhs: "Rhs"

    @log_call(
        skip_args=[
            "self",
            "gram",
            "parser",
        ],
        include_attrs=["lhs"],
        include_ctx=False,
    )
    def parse(
        self,
        gram,
        parser,
    ):
        return self.rhs.parse(
            gram,
            parser,
        )


@dataclass
class Rhs(GrammarExp):
    alts: list["Alt"]

    def parse(
        self,
        gram,
        parser,
    ):
        chkpt = parser.checkpoint()
        for a in self.alts:
            try:
                v = a.parse(
                    gram,
                    parser,
                )
            except errors.RatParseError:
                parser.restore(chkpt)
            else:
                return v

        raise errors.RatParseError.with_pos(
            parser,
            "Unexpected token",
        )

    def __or__(
        self,
        other: "Alt",
    ):
        if not isinstance(
            other,
            Alt,
        ):
            raise ValueError("Other must be Alt")

        self.alts.append(other)
        return self


@dataclass
class Alt(GrammarExp):
    exp: "Exp"
    action: str = field(default=None)

    @classmethod
    def lift(cls, obj):
        if not isinstance(obj, cls):
            return cls(obj)
        return obj

    def parse(
        self,
        gram,
        parser,
    ):
        names = {}
        v = self.exp.parse(
            gram,
            parser,
            names,
        )
        if self.action:
            if gram.header:
                old_names = dict(names)
                exec(
                    gram.header,
                    names,
                )
                names.update(old_names)  # make sure names defined in the grammar take precedent
            return eval(
                self.action,
                names,
            )
        else:
            return v

    def as_rhs(
        self,
    ):
        return Rhs([self])


@dataclass
class Exp(GrammarExp):
    _Exp_name: str | None

    def parse(
        self,
        gram,
        parser,
        names,
    ):
        v = self.exp_parse(
            gram,
            parser,
            names,
        )
        if self._Exp_name is not None:
            names[self._Exp_name] = v
        return v

    def as_alt(
        self,
        action=None,
    ):
        return Alt(
            self,
            action=action,
        )

    def star(
        self,
        name=None,
    ):
        return Star(
            name,
            self,
        )

    def then(
        self,
        other,
        name=None,
        drop_left=False,
        drop_right=False,
    ):
        return Sequence(
            name,
            self,
            other,
            drop_left=drop_left,
            drop_right=drop_right,
        )

    def optional(
        self,
        name=None,
    ):
        return Optional(
            name,
            self,
        )


@dataclass
class Boxed(Exp):
    box: "Exp"

    def parse_exp(
        self,
        gram,
        parser,
        names,
    ):
        return self.box.parse(
            gram,
            parser,
            names,
        )


@dataclass
class Optional(Exp):
    box: "Exp"

    def parse_exp(
        self,
        gram,
        parser,
        names,
    ):
        chkpt = parser.checkpoint()
        try:
            return self.box.parse(
                gram,
                parser,
                names,
            )
        except errors.RatParseError:
            parser.restore(chkpt)
            return None


@dataclass
class Sequence(Exp):
    left: "Exp"
    right: "Exp"

    drop_left: bool = False
    drop_right: bool = False

    def exp_parse(
        self,
        gram,
        parser,
        names,
    ):
        v1 = self.left.parse(
            gram,
            parser,
            names,
        )
        v2 = self.right.parse(
            gram,
            parser,
            names,
        )

        if self.drop_left:
            return v2
        elif self.drop_right:
            return v1
        else:
            return (
                v1,
                v2,
            )


@dataclass
class Star(Exp):
    pattern: "Exp"

    def exp_parse(
        self,
        gram,
        parser,
        names,
    ):
        vs = []
        while True:
            chkp = parser.checkpoint()
            try:
                v = self.pattern.parse(
                    gram,
                    parser,
                    names,
                )
            except errors.RatParseError:
                parser.restore(chkp)
                return vs
            else:
                vs.append(v)


@dataclass
class Atom(Exp):
    value: str | token_info.Token

    def exp_parse(
        self,
        gram,
        parser,
        names,
    ):
        # if it was a specific token
        if isinstance(
            self.value,
            token_info.Token,
        ):
            return parser.accept(self.value)

        # otherwise, find the rule and run it.
        return gram[self.value](parser)


def NT(
    n: str,
    name=None,
) -> Exp:
    """non-terminal"""
    return Atom(name, n)


def T(
    t: token_info.Token,
    name=None,
) -> Exp:
    return Atom(name, t)


def make_token_enum(
    tokens,
):
    ns = {
        tname: tval
        for (
            tname,
            tval,
        ) in tokens
    }
    t = type(
        "Tokens",
        (),
        ns,
    )
    return enum(t)
