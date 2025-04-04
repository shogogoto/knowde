"""neomodel label."""

from neomodel import StringProperty

from knowde.primitive.__core__.label_repo.base import LBase
from knowde.primitive.__core__.label_repo.util import LabelUtil
from knowde.tmp.definition.sentence.domain import MAX_CHARS, Sentence


class LSentence2(LBase):  # noqa: D101
    __label__ = "Sentence2"
    # Twitterのように短く読みやすい投稿を1単位としたい
    value = StringProperty(index=True, max_length=MAX_CHARS)


SentenceUtil = LabelUtil(label=LSentence2, model=Sentence)
