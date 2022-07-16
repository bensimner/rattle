import io

from hypothesis import given, strategies as st

from rattle.parsegen.grammar import (
    Grammar,
    Rule,
    Rhs,
    Alt,
    Boxed,
    Optional,
    Sequence,
    Star,
    Atom,
    NT,
    T,
)

from rattle.parsegen import token_info
from rattle.parsegen.pretty_printer import GrammarPrinter
from rattle.parsegen.metagram import MetaGram

from .parser_helpers import assert_parses_to


@st.composite
def IDENT_strategy(draw):
    return draw(st.text(alphabet="abc", min_size=1))


@st.composite
def name_strategy(draw):
    return draw(st.one_of(st.none(), IDENT_strategy()))


@st.composite
def STRING_strategy(draw):
    s = draw(st.text(alphabet="abc"))
    return f'"{s}"'


@st.composite
def NT_strategy(draw):
    n = draw(IDENT_strategy())
    name = draw(name_strategy())
    return NT(n, name)


@st.composite
def T_strategy(draw):
    return draw(
        st.sampled_from(
            [
                T(token_info.Token(token_info.TokenType.IDENT), draw(name_strategy())),
                T(token_info.Token(token_info.TokenType.STRING), draw(name_strategy())),
                T(token_info.Token(token_info.TokenType.NUMBER), draw(name_strategy())),
            ]
        )
    )


@st.composite
def Star_strategy(draw):
    return Star(draw(name_strategy()), draw(Exp_strategy()))


@st.composite
def Sequence_strategy(draw):
    return Sequence(
        draw(name_strategy()),
        draw(Exp_strategy()),
        draw(Exp_strategy()),
    )


@st.composite
def Optional_strategy(draw):
    return Optional(
        draw(name_strategy()),
        draw(Exp_strategy()),
    )


@st.composite
def Boxed_strategy(draw):
    return Boxed(
        draw(name_strategy()),
        draw(Exp_strategy()),
    )


@st.composite
def Exp_strategy(draw):
    return draw(
        st.one_of(
            Boxed_strategy(),
            Optional_strategy(),
            Sequence_strategy(),
            Star_strategy(),
            NT_strategy(),
            T_strategy(),
        )
    )


@st.composite
def Alt_strategy(draw):
    return Alt(
        draw(Exp_strategy()),
        draw(st.one_of(st.none(), STRING_strategy())),
    )


@st.composite
def Rhs_strategy(draw):
    return Rhs(
        draw(st.lists(Alt_strategy(), min_size=1)),
    )


@st.composite
def Rule_strategy(draw):
    return Rule(
        draw(IDENT_strategy()),
        draw(Rhs_strategy()),
    )


@st.composite
def Grammar_strategy(draw):
    rules = draw(st.lists(Rule_strategy(), min_size=1))
    rules = {r.lhs: r for r in rules}
    return Grammar(
        tokens=None,
        header=None,
        rules=rules,
        start_symbol=draw(IDENT_strategy()),
    )


def _test_roundtrip(g):
    f = io.StringIO()
    GrammarPrinter().pretty_print(g, f)
    assert_parses_to(MetaGram, f.getvalue(), g)


@given(Grammar_strategy())
def test_roundtrip(g):
    return _test_roundtrip(g)


if __name__ == "__main__":
    from rattle.parsegen.grammar import *
    from rattle.logging import enable

    enable()
    _test_roundtrip(
        g=Grammar(
            tokens=None,
            header=None,
            rules=[
                Rule(
                    lhs="a",
                    rhs=Rhs(
                        alts=[
                            Alt(
                                exp=Boxed(_Exp_name=None, box=Atom(_Exp_name=None, value="a")),
                                action=None,
                            )
                        ]
                    ),
                )
            ],
            start_symbol="a",
        )
    )
