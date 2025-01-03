"""label."""
from __future__ import annotations

from operator import attrgetter
from typing import Self

from neomodel import BooleanProperty, IntegerProperty, StringProperty

from knowde.primitive.__core__.domain import APIReturn, Entity
from knowde.primitive.__core__.label_repo.base import LBase, RelBase
from knowde.primitive.__core__.label_repo.rel import RelUtil
from knowde.tmp.deduction.proposition.domain import Proposition
from knowde.tmp.deduction.proposition.repo.label import LProposition


class LDeduction(LBase):
    """演繹."""

    __label__ = "Deduction"
    valid = BooleanProperty()
    text = StringProperty(index=True, required=True)


class DeductionMapper(Entity, APIReturn, frozen=True):
    """LabelのMapper."""

    valid: bool
    text: str


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
