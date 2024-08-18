"""neomodel label."""
from neomodel import StringProperty

from knowde.core.label_repo.base import LBase
from knowde.core.label_repo.util import LabelUtil
from knowde.primitive.term.domain import MAX_CHARS, Term


class LTerm(LBase):
    """用語."""

    __label__ = "Term"
    value = StringProperty(index=True, max_length=MAX_CHARS)


TermUtil = LabelUtil(label=LTerm, model=Term)
