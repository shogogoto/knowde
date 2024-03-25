from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.sentence.domain import MAX_CHARS, Sentence


class LSentence(LBase):
    __label__ = "Sentence"
    # Twitterのように短く読みやすい投稿を1単位としたい
    value = StringProperty(index=True, max_length=MAX_CHARS)


SentenceUtil = LabelUtil(label=LSentence, model=Sentence)
