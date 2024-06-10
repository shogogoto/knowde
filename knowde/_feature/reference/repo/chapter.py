from operator import attrgetter
from uuid import UUID

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.reference.domain import Chapter
from knowde._feature.reference.dto import HeadlineParam, SwapParam
from knowde._feature.reference.repo.label import (
    BookUtil,
    ChapterUtil,
    RelChapterBookUtil,
)


def add_book_chapter(book_uid: UUID, p: HeadlineParam) -> Chapter:
    book = BookUtil.find_by_id(book_uid)
    chap = ChapterUtil.create(title=p.title)
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
    p: HeadlineParam,
) -> Chapter:
    ChapterUtil.change(uid=chap_uid, title=p.title)
    rel = RelChapterBookUtil.find_by_source_id(chap_uid)[0]
    return Chapter.from_rel(rel=rel)


def remove_chapter(chap_uid: UUID) -> None:
    """兄弟chapterをreorderして配下sectionを削除."""
    rels = query_cypher(
        """
        MATCH (tgt:Chapter {uid: $uid})-[:COMPOSE]->(r:Reference)
        OPTIONAL MATCH (tgt)<-[:COMPOSE]-(s:Section)
        DETACH DELETE tgt, s
        WITH r
        OPTIONAL MATCH (r)<-[rel:COMPOSE]-(c:Chapter)
        RETURN rel
        """,
        params={"uid": chap_uid.hex},
    ).get("rel")
    rels = [rel for rel in rels if rel]  # exlcude None
    rels = sorted(rels, key=attrgetter("order"))
    for i, rel in enumerate(rels):
        rel.order = i
        rel.save()


def complete_chapter(pref_uid: str) -> Chapter:
    lb = ChapterUtil.complete(pref_uid)
    m = lb.to_model()
    rel = RelChapterBookUtil.find_by_source_id(m.valid_uid)[0]
    return Chapter.from_rel(rel)
