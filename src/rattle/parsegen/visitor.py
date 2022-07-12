from dataclasses import (
    fields,
)

from rattle.parsegen import (
    grammar,
)


class GrammarWalker:
    def visit(
        self,
        node,
        **kws,
    ):
        k = type(node).__name__

        func = getattr(
            self,
            f"visit_{k}",
            None,
        )
        if func is not None:
            return func(
                node,
                **kws,
            )
        else:
            self.generic_visit(node)

    def generic_visit(self, node):
        for f in fields(type(node)):
            v = getattr(
                node,
                f.name,
            )

            if isinstance(
                v,
                grammar.GrammarExp,
            ):
                self.visit(v)
            elif isinstance(
                v,
                list,
            ):
                for e in v:
                    if isinstance(
                        e,
                        grammar.GrammarExp,
                    ):
                        self.visit(e)
            elif isinstance(
                v,
                grammar.Grammar,
            ):
                for r in v.rules.values():
                    self.visit(r)
            else:
                pass
