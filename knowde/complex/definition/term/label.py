"""neomodel label."""
from neomodel import StringProperty

from knowde.complex.definition.term.domain import MAX_CHARS, Term
from knowde.core.label_repo.base import LBase
from knowde.core.label_repo.util import LabelUtil


class LTerm(LBase):
    """用語."""

    __label__ = "Term"
    value = StringProperty(index=True, max_length=MAX_CHARS)


TermUtil = LabelUtil(label=LTerm, model=Term)
