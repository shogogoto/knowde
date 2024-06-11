from __future__ import annotations

from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.chapter import (
    add_book_chapter,
    change_chapter,
    remove_chapter,
    swap_chapter_order,
)
from knowde._feature.reference.repo.label import BookUtil
from knowde._feature.reference.repo.reference import find_reftree


def h(s: str) -> HeadlineParam:
    return HeadlineParam(title=s)


def test_swap_chapter() -> None:
    """章の順番を入れ替える."""
    book = BookUtil.create(title="book")
    b = book.to_model()
    add_book_chapter(b.valid_uid, h("h1"))
    add_book_chapter(b.valid_uid, h("h2"))
    tree1 = find_reftree(b.valid_uid)
    assert [c.title for c in tree1.chapters] == ["h1", "h2"]

    swap_chapter_order(b.valid_uid, SwapParam.create(0, 1))
    tree2 = find_reftree(b.valid_uid)
    assert [c.title for c in tree2.chapters] == ["h2", "h1"]

    add_book_chapter(b.valid_uid, h("h3"))
    tree3 = find_reftree(b.valid_uid)
    assert [c.title for c in tree3.chapters] == ["h2", "h1", "h3"]


def test_crud_chapter() -> None:
    b = BookUtil.create(title="book").to_model()
    c1 = add_book_chapter(b.valid_uid, h("h1"))
    c2 = change_chapter(c1.valid_uid, h("h2"))
    assert c2.title == "h2"
    assert c1.valid_uid == c2.valid_uid
    tree = find_reftree(b.valid_uid)
    assert tree.chapters[0].chapter == c2

    c = add_book_chapter(b.valid_uid, h("h3"))
    add_book_chapter(b.valid_uid, h("h4"))
    remove_chapter(c.valid_uid)

    tree = find_reftree(b.valid_uid)
    chaps = tree.chapters
    assert [c.title for c in chaps] == ["h2", "h4"]


# def test_find_parent_of_chapter() -> None:
#     b = BookUtil.create(title="book").to_model()
#     c1 = add_book_chapter(b.valid_uid, h("h1"))
#     c2 = add_book_chapter(b.valid_uid, h("h2"))
#     print("#################################")
#     print("#################################")
#     print("#################################")
#     find_reftree2(c1.valid_uid)
#     # assert tree1.root == b
