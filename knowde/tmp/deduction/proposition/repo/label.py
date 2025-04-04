"""neomodel label."""

from neomodel import StringProperty

from knowde.primitive.__core__.label_repo.base import LBase
from knowde.primitive.__core__.label_repo.util import LabelUtil
from knowde.tmp.deduction.proposition.domain import Proposition


class LProposition(LBase):
    """命題."""

    __label__ = "Proposition"
    text = StringProperty(index=True)


PropositionUtil = LabelUtil(label=LProposition, model=Proposition)
