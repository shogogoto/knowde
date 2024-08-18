from neomodel import StringProperty

from knowde._feature.sentence.domain import MAX_CHARS, Sentence
from knowde.core.repo.base import LBase
from knowde.core.repo.util import LabelUtil


class LSentence(LBase):
    __label__ = "Sentence"
    # Twitterのように短く読みやすい投稿を1単位としたい
    value = StringProperty(index=True, max_length=MAX_CHARS)


SentenceUtil = LabelUtil(label=LSentence, model=Sentence)
