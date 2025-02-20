"""neomodel label."""
from neomodel import StringProperty

from knowde.primitive.__core__.label_repo.base import LBase
from knowde.primitive.__core__.label_repo.util import LabelUtil
from knowde.tmp.definition.term.domain import MAX_CHARS, Term


class LTerm2(LBase):
    """用語."""

    __label__ = "Term2"
    value = StringProperty(index=True, max_length=MAX_CHARS)


TermUtil = LabelUtil(label=LTerm2, model=Term)
