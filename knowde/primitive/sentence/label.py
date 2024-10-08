"""neomodel label."""
from neomodel import StringProperty

from knowde.core.label_repo.base import LBase
from knowde.core.label_repo.util import LabelUtil
from knowde.primitive.sentence.domain import MAX_CHARS, Sentence


class LSentence(LBase):  # noqa: D101
    __label__ = "Sentence"
    # Twitterのように短く読みやすい投稿を1単位としたい
    value = StringProperty(index=True, max_length=MAX_CHARS)


SentenceUtil = LabelUtil(label=LSentence, model=Sentence)
