"""neomodel label."""
from neomodel import StringProperty

from knowde.complex.definition.sentence.domain import MAX_CHARS, Sentence
from knowde.core.label_repo.base import LBase
from knowde.core.label_repo.util import LabelUtil


class LSentence(LBase):  # noqa: D101
    __label__ = "Sentence"
    # Twitterのように短く読みやすい投稿を1単位としたい
    value = StringProperty(index=True, max_length=MAX_CHARS)


SentenceUtil = LabelUtil(label=LSentence, model=Sentence)
