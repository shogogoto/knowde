from __future__ import annotations

from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.book import find_reftree
from knowde._feature.reference.repo.chapter import (
    add_book_chapter,
    swap_chapter_order,
)
from knowde._feature.reference.repo.label import BookUtil


def h(s: str) -> HeadlineParam:
    return HeadlineParam(value=s)


def test_swap_chapter() -> None:
    """章の順番を入れ替える."""
    book = BookUtil.create(title="book1")
    b = book.to_model()
    add_book_chapter(b.valid_uid, h("h1"))
    add_book_chapter(b.valid_uid, h("h2"))
    tree1 = find_reftree(b.valid_uid)
    assert [c.value for c in tree1.chapters] == ["h1", "h2"]

    swap_chapter_order(b.valid_uid, SwapParam.create(0, 1))
    tree2 = find_reftree(b.valid_uid)
    assert [c.value for c in tree2.chapters] == ["h2", "h1"]
