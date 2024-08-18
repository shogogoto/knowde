"""test for ref def."""


from uuid import UUID

from pytest_unordered import unordered

from knowde._feature.reference.dto import BookParam
from knowde._feature.reference.repo.book import add_book
from knowde.complex.definition.repo.definition import add_definition, list_definitions
from knowde.reference.dto import RefDefParam
from knowde.reference.repo.definition import (
    add_refdef,
    connect_def2ref,
    disconnect_refdef,
    list_refdefs,
)


def _p(uid: UUID, name: str, explain: str) -> RefDefParam:
    return RefDefParam(ref_uid=uid, name=name, explain=explain)


def test_add_refdef() -> None:
    """引用付き定義追加."""
    book = add_book(BookParam(title="ref"))
    d1 = add_refdef(_p(book.valid_uid, "def1", "e1")).df
    d2 = add_refdef(_p(book.valid_uid, "def2", "e2")).df
    rd = list_refdefs(book.valid_uid)

    assert rd.book == book
    assert rd.defs.defs == unordered([d1, d2])


def test_connect_def2ref_and_disconnect() -> None:
    """定義を参考に紐付けて解除する."""
    book = add_book(BookParam(title="ref"))
    d1 = add_definition(name="d1", explain="e1")
    d2 = add_definition(name="d2", explain="e2")
    d3 = add_definition(name="d3", explain="e3")

    uids = [d.valid_uid for d in [d1, d2, d3]]
    connect_def2ref(book.valid_uid, uids)

    rd = list_refdefs(book.valid_uid)
    assert rd.book == book
    assert rd.defs.defs == unordered([d1, d2, d3])

    disconnect_refdef(book.valid_uid, uids[0:2])
    rd = list_refdefs(book.valid_uid)
    assert rd.defs.defs == [d3]

    # relは削除されたけど定義自体は削除しない
    assert list_definitions().defs == unordered([d1, d2, d3])
