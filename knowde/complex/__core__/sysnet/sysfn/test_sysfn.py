"""test."""


import pytest

from knowde.complex.__core__.sysnet.errors import SentenceConflictError

from . import check_duplicated_sentence


def test_duplicate_sentence() -> None:
    """文重複."""
    with pytest.raises(SentenceConflictError):
        check_duplicated_sentence(["aaa", "aaa"])
