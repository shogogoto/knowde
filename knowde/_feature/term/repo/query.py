from __future__ import annotations

from knowde._feature.term.domain import Term

from .label import LTerm


class TermQuery:
    @staticmethod
    def find(v: str) -> list[Term]:
        """{name}を含むデータすべてを取得."""
        lbs = LTerm.nodes.filter(value__icontains=v)
        return Term.to_models(lbs)

    @staticmethod
    def find_one_or_none(v: str) -> Term | None:
        lb = LTerm.nodes.get_or_none(value__icontains=v)
        if lb is None:
            return None
        return Term.to_model(lb)
