from __future__ import annotations

from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.book import find_reftree
from knowde._feature.reference.repo.chapter import (
    add_book_chapter,
    change_chapter,
    remove_chapter,
    swap_chapter_order,
)
from knowde._feature.reference.repo.label import BookUtil


def h(s: str) -> HeadlineParam:
    return HeadlineParam(value=s)


def test_swap_chapter() -> None:
    """章の順番を入れ替える."""
    book = BookUtil.create(title="book")
    b = book.to_model()
    add_book_chapter(b.valid_uid, h("h1"))
    add_book_chapter(b.valid_uid, h("h2"))
    tree1 = find_reftree(b.valid_uid)
    assert [c.value for c in tree1.chapters] == ["h1", "h2"]

    swap_chapter_order(b.valid_uid, SwapParam.create(0, 1))
    tree2 = find_reftree(b.valid_uid)
    assert [c.value for c in tree2.chapters] == ["h2", "h1"]

    add_book_chapter(b.valid_uid, h("h3"))
    tree3 = find_reftree(b.valid_uid)
    assert [c.value for c in tree3.chapters] == ["h2", "h1", "h3"]


def test_crud_chapter() -> None:
    b = BookUtil.create(title="book").to_model()
    c1 = add_book_chapter(b.valid_uid, h("h1"))
    c2 = change_chapter(c1.valid_uid, value="h2")
    assert c2.value == "h2"
    assert c1.valid_uid == c2.valid_uid
    tree = find_reftree(b.valid_uid)
    assert tree.chapters == [c2]

    remove_chapter(c2.valid_uid)
    tree = find_reftree(b.valid_uid)
    assert tree.chapters == []