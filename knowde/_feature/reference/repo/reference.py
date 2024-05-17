from __future__ import annotations

from operator import attrgetter, itemgetter
from uuid import UUID  # noqa: TCH003

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.reference.domain import (
    Book,
    Chapter,
    ReferenceTree,
    RefType,
    Section,
    Web,
)
from knowde._feature.reference.repo.label import LBook, LReference


def to_refmodel(r: LReference) -> tuple[Book | Web, RefType]:
    if isinstance(r, LBook):
        return Book.to_model(r), RefType.Book
    return Web.to_model(r), RefType.Web


def find_reftree(ref_uid: UUID) -> ReferenceTree:
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

    ref, t = res.get("r", convert=to_refmodel)[0]

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
        root=ref,
        chapters=sorted(chaps, key=attrgetter("order")),
        reftype=t,
    )


def remove_ref(ref_uid: UUID) -> None:
    """本配下を削除."""
    query_cypher(
        """
        MATCH (tgt:Reference {uid: $uid})
        OPTIONAL MATCH (tgt)<-[:COMPOSE]-(c:Chapter)
        OPTIONAL MATCH (c)<-[:COMPOSE]-(s:Section)
        DETACH DELETE tgt, c, s
        """,
        params={"uid": ref_uid.hex},
    )
