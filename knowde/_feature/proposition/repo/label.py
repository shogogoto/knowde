from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.proposition.domain import Proposition


class LProposition(LBase):
    """命題."""

    __label__ = "Proposition"
    text = StringProperty(index=True)


PropositionUtil = LabelUtil(label=LProposition, model=Proposition)
