"""test for ref def."""


from uuid import UUID

from pytest_unordered import unordered

from knowde._feature.reference.dto import BookParam
from knowde._feature.reference.repo.book import add_book
from knowde.reference.dto import RefDefParam
from knowde.reference.repo.definition import add_refdef, list_refdefs


def _p(uid: UUID, name: str, explain: str) -> RefDefParam:
    return RefDefParam(ref_uid=uid, name=name, explain=explain)


def test_add_refdef() -> None:
    """引用付き定義追加."""
    book = add_book(BookParam(title="ref"))
    d1, _ = add_refdef(_p(book.valid_uid, "def1", "e1"))
    d2, _ = add_refdef(_p(book.valid_uid, "def2", "e2"))
    rd = list_refdefs()[0]
    assert rd.book == book
    assert rd.defs == unordered([d1, d2])
