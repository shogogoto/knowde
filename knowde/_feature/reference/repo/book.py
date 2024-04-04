from operator import attrgetter, itemgetter
from uuid import UUID

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.reference.domain import Book, Chapter, ReferenceTree, Section
from knowde._feature.reference.dto import BookParam, PartialBookParam

from .label import BookUtil


# add and change bookはauthorとの絡みがあるため、
#  advanced featureへ移動するかも
def add_book(p: BookParam) -> Book:
    """同じタイトルでも作者が別なら許容される."""
    if BookUtil.find_one_or_none(title=p.title):
        msg = f"「{p.title}」は既に登録済みです."
        raise AlreadyExistsError(msg)
    return BookUtil.create(**p.model_dump()).to_model()


def remove_book(uid: UUID) -> None:
    """本配下を削除."""
    query_cypher(
        """
        MATCH (tgt:Reference {uid: $uid})
        OPTIONAL MATCH (tgt)<-[:COMPOSE]-(c:Chapter)
        OPTIONAL MATCH (c)<-[:COMPOSE]-(s:Section)
        DETACH DELETE tgt, c, s
        """,
        params={"uid": uid.hex},
    )


def change_book(ref_uid: UUID, p: PartialBookParam) -> Book:
    return BookUtil.change(uid=ref_uid, **p.model_dump()).to_model()


def find_reftree(ref_uid: UUID) -> ReferenceTree[Book]:
    res = query_cypher(
        """
        MATCH (r:Reference {uid: $uid})
        // Chapterが親を1つだけ持つneomodel制約Oneのためのedgeの向き
        OPTIONAL MATCH (b)<-[crel:COMPOSE]-(c:Chapter)
        OPTIONAL MATCH (c)<-[srel:COMPOSE]-(:Section)
        RETURN
            r,
            crel,
            collect(srel) as srels
        """,
        params={"uid": ref_uid.hex},
    )
    book = res.get("r", convert=Book.to_model)[0]
    chaps = []
    for c, srels in zip(
        res.get("crel"),
        res.get("srels", row_convert=itemgetter(0)),
    ):
        if c is None:
            continue
        secs = [Section.from_rel(rel) for rel in srels]
        chap = Chapter.from_rel(c, sorted(secs, key=attrgetter("order")))
        chaps.append(chap)
    return ReferenceTree(
        root=book,
        chapters=sorted(chaps, key=attrgetter("order")),
    )
