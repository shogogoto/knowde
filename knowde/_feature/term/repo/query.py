from __future__ import annotations

from knowde._feature._shared.repo.label import Label, Labels
from knowde._feature.term.domain import Term

from .label import LTerm


class TermQuery:
    @staticmethod
    def find(v: str) -> Labels[LTerm, Term]:
        """{name}を含むデータすべてを取得."""
        lbs = LTerm.nodes.filter(value__icontains=v)
        return Labels(root=lbs, model=Term)

    @staticmethod
    def find_one_or_none(v: str) -> Label[LTerm, Term] | None:
        lb = LTerm.nodes.get_or_none(value=v)
        if lb is None:
            return None
        return Label(label=lb, model=Term)
