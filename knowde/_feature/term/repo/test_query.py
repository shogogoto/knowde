"""既存の用語を探す."""

from knowde._feature.term.repo.query import TermQuery

from .label import term_util


def test_find_by_name() -> None:
    t = term_util.create(value="term1").to_model()
    assert t in TermQuery.find("1")
    assert t not in TermQuery.find("term12")
