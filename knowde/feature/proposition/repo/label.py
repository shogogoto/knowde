"""label."""
from __future__ import annotations

from operator import attrgetter
from typing import Self

from neomodel import BooleanProperty, IntegerProperty, StringProperty

from knowde._feature._shared.repo.base import LBase, RelBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.util import LabelUtil
from knowde.feature.proposition.domain import Proposition


class LProposition(LBase):
    """命題."""

    __label__ = "Proposition"
    text = StringProperty(index=True)


class LDeduction(LBase):
    """演繹."""

    __label__ = "Deduction"
    valid = BooleanProperty()
    text = StringProperty(index=True)


class RelPremise(RelBase):
    """順序付き前提関係."""

    order = IntegerProperty()

    @classmethod
    def sort(cls, ls: list[Self]) -> list[Proposition]:
        """Sort by order."""
        rels = sorted(ls, key=attrgetter("order"))
        return [Proposition.to_model(rel.start_node()) for rel in rels]


REL_CONCLUSION_LABEL = "CONCLUDE"
REL_PREMISE_LABEL = "PREMISE"

RelPremiseUtil = RelUtil(
    t_source=LDeduction,
    t_target=LProposition,
    name=REL_PREMISE_LABEL,
    t_rel=RelPremise,
)


PropositionUtil = LabelUtil(label=LProposition, model=Proposition)
