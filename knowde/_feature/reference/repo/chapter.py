from uuid import UUID

from knowde._feature.reference.domain import Chapter
from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.label import (
    BookUtil,
    ChapterUtil,
    RelChapterBookUtil,
)


def add_book_chapter(book_uid: UUID, p: HeadlineParam) -> Chapter:
    book = BookUtil.find_by_id(book_uid)
    chap = ChapterUtil.create(value=p.value)
    count = RelChapterBookUtil.count_sources(book_uid)
    rel = RelChapterBookUtil.connect(chap.label, book.label, order=count)
    return Chapter.from_rel(rel)


def swap_chapter_order(book_uid: UUID, p: SwapParam) -> None:
    rels = RelChapterBookUtil.find_by_target_id(book_uid)
    rel1 = next(filter(lambda x: x.order == p.order1, rels))
    rel2 = next(filter(lambda x: x.order == p.order2, rels))
    rel1.order = p.order2
    rel2.order = p.order1
    rel1.save()
    rel2.save()


def change_chapter(
    chap_uid: UUID,
    value: str,
) -> Chapter:
    ChapterUtil.change(uid=chap_uid, value=value)
    rel = RelChapterBookUtil.find_by_source_id(chap_uid)[0]
    return Chapter.from_rel(rel=rel)


def remove_chapter(chap_uid: UUID) -> None:
    """配下のSectionsも一緒に削除するバージョンも欲しい."""
    ChapterUtil.delete(chap_uid)