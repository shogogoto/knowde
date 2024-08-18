from neomodel import StringProperty

from knowde._feature.term.domain import MAX_CHARS, Term
from knowde.core.repo.base import LBase
from knowde.core.repo.util import LabelUtil


class LTerm(LBase):
    __label__ = "Term"
    value = StringProperty(index=True, max_length=MAX_CHARS)


TermUtil = LabelUtil(label=LTerm, model=Term)
