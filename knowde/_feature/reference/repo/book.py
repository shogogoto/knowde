from operator import attrgetter, itemgetter
from uuid import UUID

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.reference.domain import Book, Chapter, ReferenceTree
from knowde._feature.reference.dto import BookParam, PartialBookParam

from .label import BookUtil


# add and change bookはauthorとの絡みがあるため、
#  advanced featureへ移動するかも
def add_book(p: BookParam) -> Book:
    """同じタイトルでも作者が別なら許容される."""
    if BookUtil.find_one_or_none(title=p.title):
        msg = f"「{p.title}」は既に登録済みです."
        raise AlreadyExistsError(msg)
    return BookUtil.create(title=p.title).to_model()


def remove_book(uid: UUID) -> None:
    """本配下を削除."""
    BookUtil.delete(uid)


def change_book(uid: UUID, p: PartialBookParam) -> Book:
    return BookUtil.change(uid=uid, **p.model_dump()).to_model()


def find_reftree(book_uid: UUID) -> ReferenceTree[Book]:
    res = query_cypher(
        """
        MATCH (b:Book {uid: $uid})
        // Chapterが親を1つだけ持つneomodel制約Oneのためのedgeの向き
        OPTIONAL MATCH (b)<-[crel:COMPOSE]-(c:Chapter)
        OPTIONAL MATCH (c)<-[:COMPOSE]-(s:Section)
        RETURN
            b,
            crel,
            collect(s) as secs
        """,
        params={"uid": book_uid.hex},
    )
    book = res.get("b", convert=Book.to_model)[0]
    chaps = []
    for c, secs in zip(
        res.get("crel"),
        res.get("secs", row_convert=itemgetter(0)),
    ):
        chap = Chapter.from_rel(c, secs)
        chaps.append(chap)
    return ReferenceTree(
        root=book,
        chapters=sorted(chaps, key=attrgetter("order")),
    )
