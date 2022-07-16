from rattle.utils.enums import (
    enum,
)
from rattle.parsegen.token_info import (
    TokenType,
    Token,
)

# for the metagram grammar definition
from rattle.parsegen.grammar import (
    grammar,
    NT,
    T,
)

MetaGram_header = """\
# for the metagram actions
from rattle.parsegen.grammar import *
"""


@grammar
class MetaGram:
    @enum
    class Tokens(TokenType):
        ASSIGN = ":="
        ALT = "|"
        LBRACE = "{"
        RBRACE = "}"
        SEMICOLON = ";"
        COMMA = ","
        EQ = "="
        LPAREN = "("
        RPAREN = ")"

    header = MetaGram_header
    start_symbol = "grammar"

    grammar = (
        (
            NT("header_lines", "hds",).then(
                NT(
                    "rules",
                    "rules",
                )
            )
        )
        .as_alt(action="Grammar.from_header_and_rules(hds, rules).normalize()")
        .as_rhs()
    )

    header_lines = NT("header_line").star().as_alt().as_rhs()

    header_line = (
        NT(
            "header_rule",
            "s",
        )
        .as_alt(action='{"header": s}')
        .as_rhs()
        | NT(
            "start_symbol_rule",
            "s",
        ).as_alt(action='{"start_symbol": s}')
        | NT(
            "tokens_rule",
            "toks",
        ).as_alt(action='{"tokens": toks}')
    )

    header_rule = (
        (
            T(
                Token(
                    Tokens.IDENT,
                    "@header",
                )
            )
            .then(T(Token(Tokens.ASSIGN)))
            .then(
                T(
                    Token(Tokens.STRING),
                    "s",
                )
            )
            .then(T(Token(Tokens.SEMICOLON)))
        )
        .as_alt(action="s.value")
        .as_rhs()
    )

    start_symbol_rule = (
        (
            T(
                Token(
                    Tokens.IDENT,
                    "@start_symbol",
                )
            )
            .then(T(Token(Tokens.ASSIGN)))
            .then(
                T(
                    Token(Tokens.IDENT),
                    "s",
                )
            )
            .then(T(Token(Tokens.SEMICOLON)))
        )
        .as_alt(action="s.value")
        .as_rhs()
    )

    tokens_rule = (
        (
            T(
                Token(
                    Tokens.IDENT,
                    "@tokens",
                )
            )
            .then(T(Token(Tokens.ASSIGN)))
            .then(
                NT(
                    "enum",
                    "enum",
                )
            )
            .then(T(Token(Tokens.SEMICOLON)))
        )
        .as_alt(action="make_token_enum(enum)")
        .as_rhs()
    )

    enum = (
        (T(Token(Tokens.LBRACE)).then(NT("enum_line").star("enums")).then(T(Token(Tokens.RBRACE))))
        .as_alt(action="enums")
        .as_rhs()
    )

    enum_line = (
        (
            T(
                Token(Tokens.IDENT),
                "n",
            )
            .then(T(Token(Tokens.EQ)))
            .then(
                T(
                    Token(Tokens.STRING),
                    "s",
                )
            )
            .then(T(Token(Tokens.COMMA)))
        )
        .as_alt(action="(n.value, s.string_value)")
        .as_rhs()
    )

    rules = NT("rule").star("rules").as_alt(action="{r.lhs: r for r in rules}").as_rhs()
    rule = (
        (
            T(
                Token(Tokens.IDENT),
                "name",
            )
            .then(T(Token(Tokens.ASSIGN)))
            .then(
                NT(
                    "rule_body",
                    "body",
                )
            )
            .then(T(Token(Tokens.SEMICOLON)))
        )
        .as_alt(action="Rule(name.value, rhs=body)")
        .as_rhs()
    )

    rule_body = (
        (
            NT("alt", "first",).then(
                (
                    T(Token(Tokens.ALT)).then(
                        NT("alt"),
                        drop_left=True,
                    )
                ).star("rest")
            )
        )
        .as_alt(action="Rhs([first, *rest])")
        .as_rhs()
    )

    alt = (
        NT(
            "rule_expr",
            "body",
        )
        .then(T(Token(Tokens.LBRACE)))
        .then(
            T(
                Token(Tokens.STRING),
                "action",
            )
        )
        .then(T(Token(Tokens.RBRACE)))
    ).as_alt(action="Alt(body, action.value)").as_rhs() | (
        NT(
            "rule_expr",
            "body",
        )
    ).as_alt(
        action="Alt(body)"
    )

    rule_assign_part = (
        (
            T(
                Token(Tokens.IDENT),
                "name",
            )
            .then(T(Token(Tokens.EQ)))
            .then(
                NT(
                    "rule_expr",
                    "body",
                )
            )
        )
        .as_alt(action="Boxed(name.value, body)")
        .as_rhs()
    )

    rule_expr = (
        NT(
            "rule_expr_part",
            "lhs",
        )
        .then(
            NT(
                "rule_expr",
                "rhs",
            )
        )
        .as_alt(action="Sequence(None, lhs, rhs)")
        .as_rhs()
        | NT("rule_expr_part").as_alt()
    )

    rule_expr_part = NT("rule_assign_part").as_alt().as_rhs() | NT("atom").as_alt()

    atom = (
        T(
            Token(Tokens.IDENT),
            "t",
        )
        .as_alt(action="NT(t.value)")
        .as_rhs()
        | T(
            Token(Tokens.STRING),
            "t",
        ).as_alt(action="t.value")
        | T(Token(Tokens.LPAREN))
        .then(
            NT(
                "rule_expr",
                "body",
            )
        )
        .then(T(Token(Tokens.RPAREN)))
        .as_alt(action="body")
    )


if __name__ == "__main__":
    from rattle.parsegen.pretty_printer import GrammarPrinter

    print("# generated by metagram.py")
    print()
    GrammarPrinter().pretty_print(MetaGram)
