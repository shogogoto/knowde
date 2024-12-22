"""neomodel label."""
from neomodel import StringProperty

from knowde.complex.deduction.proposition.domain import Proposition
from knowde.primitive.__core__.label_repo.base import LBase
from knowde.primitive.__core__.label_repo.util import LabelUtil


class LProposition(LBase):
    """命題."""

    __label__ = "Proposition"
    text = StringProperty(index=True)


PropositionUtil = LabelUtil(label=LProposition, model=Proposition)
