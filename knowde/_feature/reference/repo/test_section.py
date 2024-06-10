from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.chapter import add_book_chapter, remove_chapter
from knowde._feature.reference.repo.label import BookUtil, SectionUtil
from knowde._feature.reference.repo.reference import find_reftree
from knowde._feature.reference.repo.section import (
    add_section,
    remove_section,
    swap_section_order,
)


def h(s: str) -> HeadlineParam:
    return HeadlineParam(title=s)


def test_swap_section() -> None:
    book = BookUtil.create(title="book")
    b = book.to_model()
    c = add_book_chapter(b.valid_uid, h("h1"))
    s1 = add_section(c.valid_uid, h("s1"))
    s2 = add_section(c.valid_uid, h("s2"))
    tree = find_reftree(b.valid_uid)
    assert tree.chapters[0].sections == [s1, s2]

    swap_section_order(c.valid_uid, SwapParam.create(0, 1))
    tree2 = find_reftree(b.valid_uid)
    secs = tree2.chapters[0].sections
    assert [s.title for s in secs] == ["s2", "s1"]


def test_remove_section_and_reorder() -> None:
    book = BookUtil.create(title="book")
    b = book.to_model()
    c = add_book_chapter(b.valid_uid, h("h1"))
    s1 = add_section(c.valid_uid, h("s1"))
    _s2 = add_section(c.valid_uid, h("s2"))
    s3 = add_section(c.valid_uid, h("s3"))
    _s4 = add_section(c.valid_uid, h("s4"))

    remove_section(s1.valid_uid)
    tree = find_reftree(b.valid_uid)
    secs = tree.chapters[0].sections
    assert [s.title for s in secs] == ["s2", "s3", "s4"]
    assert [s.order for s in secs] == [0, 1, 2]

    remove_section(s3.valid_uid)
    tree = find_reftree(b.valid_uid)
    secs = tree.chapters[0].sections
    assert [s.title for s in secs] == ["s2", "s4"]
    assert [s.order for s in secs] == [0, 1]


def test_remove_chapter_with_sections() -> None:
    book = BookUtil.create(title="book")
    b = book.to_model()
    c1 = add_book_chapter(b.valid_uid, h("h1"))
    add_section(c1.valid_uid, h("s11"))
    add_section(c1.valid_uid, h("s12"))
    add_section(c1.valid_uid, h("s13"))
    c2 = add_book_chapter(b.valid_uid, h("h2"))
    s = add_section(c2.valid_uid, h("s21"))

    tree = find_reftree(b.valid_uid)
    assert len(tree.chapters) == 2  # noqa: PLR2004

    remove_chapter(c1.valid_uid)

    tree = find_reftree(b.valid_uid)
    assert len(tree.chapters) == 1
    founds = SectionUtil.find()
    assert len(founds) == 1
    assert founds[0].title == s.title
