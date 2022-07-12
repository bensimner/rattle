import sys
from dataclasses import (
    fields,
)
from textwrap import (
    dedent,
)

from rattle.parsegen import (
    grammar,
)
from rattle.parsegen import (
    visitor,
)
from rattle.parsegen.token_info import (
    Token,
    TokenType,
)


class GrammarPrinter(visitor.GrammarWalker):
    def pretty_print(
        self,
        grammar,
        file=sys.stdout,
    ):
        self._pprint_headers(
            grammar,
            file,
        )

    def _pprint_headers(
        self,
        grammar,
        file,
    ):
        self._pprint_tokens(
            grammar,
            file,
        )
        self._pprint_header(
            grammar,
            file,
        )
        self._pprint_start_symbol(
            grammar,
            file,
        )
        self._pprint_rules(
            grammar,
            file,
        )

    def _pprint_tokens(
        self,
        grammar,
        file,
    ):
        if grammar.tokens is None:
            return

        tokens = list(grammar.tokens.members())
        tokens = ",\n                ".join(f"{t.name}={t.value}" for t in tokens)
        file.write(
            dedent(
                f"""\
            @tokens := {{
                {tokens}
            }};\n\n"""
            )
        )

    def _pprint_header(
        self,
        grammar,
        file,
    ):
        if grammar.header is None:
            return

        file.write(f'@header := "{grammar.header}";\n\n')

    def _pprint_start_symbol(
        self,
        grammar,
        file,
    ):
        file.write(f"@start_symbol := {grammar.start_symbol};\n\n")

    def _pprint_rules(
        self,
        grammar,
        file,
    ):
        for rule in sorted(
            grammar.rules.values(),
            key=lambda r: r.lhs,
        ):
            rhs = self.visit(rule.rhs)
            file.write(f"{rule.lhs} := {rhs};\n")

    def visit_Rhs(self, node):
        alts = [self.visit(a) for a in node.alts]
        return "|".join(alts)

    def visit_Alt(self, node):
        v = self.visit(node.exp)
        if node.action is not None:
            return f"{v} {{ {node.action} }}"
        else:
            return f"{v}"

    def _exp_name(self, node):
        if node._Exp_name is not None:
            return f"{node._Exp_name}="
        return ""

    def visit_Boxed(self, node):
        v = self.visit(node.box)
        return f"{self._exp_name(node)}{v}"

    def visit_Optional(self, node):
        v = self.visit(node.box)
        return f"{self._exp_name(node)}{v}?"

    def visit_Sequence(self, node):
        v1 = self.visit(node.left)
        v2 = self.visit(node.right)
        return f"{self._exp_name(node)}({v1} {v2})"

    def visit_Star(self, node):
        v = self.visit(node.pattern)
        return f"{self._exp_name(node)}{v}*"

    def visit_NonTerminal(self, node):
        return f"{self._exp_name(node)}{node.name}"

    def visit_Atom(self, node):
        if isinstance(
            node.value,
            Token,
        ):
            token = node.value
            if token.value is not None and isinstance(
                token.value,
                str,
            ):
                return f'{self._exp_name(node)}"{token.value}"'
            else:
                return f"{self._exp_name(node)}{token.token_type.name}"
        else:
            return f"{self._exp_name(node)}{node.value}"

    def generic_visit(self, node):
        raise ValueError(node)
