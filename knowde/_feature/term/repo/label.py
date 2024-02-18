from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.term.domain import MAX_CHARS, Term


class LTerm(LBase):
    __label__ = "Term"
    value = StringProperty(max_length=MAX_CHARS)


term_util = LabelUtil(label=LTerm, model=Term)
