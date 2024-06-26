"""label."""

from neomodel import BooleanProperty, StringProperty

from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.sentence.label import LSentence
from knowde.feature.proposition.domain import Proposition


class LProposition(LSentence):
    """命題."""

    __label__ = "Proposition"
    name = StringProperty(index=True)


class LArgument(LSentence):
    """論証."""

    __label__ = "Argument"
    boolean = BooleanProperty()


PropositionUtil = LabelUtil(label=LProposition, model=Proposition)
