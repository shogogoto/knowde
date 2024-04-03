from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.book import find_reftree
from knowde._feature.reference.repo.chapter import add_book_chapter
from knowde._feature.reference.repo.label import BookUtil
from knowde._feature.reference.repo.section import add_section, swap_section_order


def h(s: str) -> HeadlineParam:
    return HeadlineParam(value=s)


def test_swap_section() -> None:
    book = BookUtil.create(title="book")
    b = book.to_model()
    c = add_book_chapter(b.valid_uid, h("h1"))
    s1 = add_section(c.valid_uid, h("sec1"))
    s2 = add_section(c.valid_uid, h("sec2"))
    tree = find_reftree(b.valid_uid)
    assert tree.chapters[0].sections == [s1, s2]

    swap_section_order(c.valid_uid, SwapParam.create(0, 1))
    tree2 = find_reftree(b.valid_uid)
    secs = tree2.chapters[0].sections
    assert [s.value for s in secs] == ["sec2", "sec1"]
