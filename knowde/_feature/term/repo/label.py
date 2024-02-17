from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature.term.domain import MAX_CHARS


class LTerm(LBase):
    __label__ = "Term"
    value = StringProperty(max_length=MAX_CHARS)
