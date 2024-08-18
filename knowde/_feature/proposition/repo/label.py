from neomodel import StringProperty

from knowde._feature.proposition.domain import Proposition
from knowde.core.repo.base import LBase
from knowde.core.repo.util import LabelUtil


class LProposition(LBase):
    """命題."""

    __label__ = "Proposition"
    text = StringProperty(index=True)


PropositionUtil = LabelUtil(label=LProposition, model=Proposition)
