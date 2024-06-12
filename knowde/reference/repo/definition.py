"""referenceとpersonに依存."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from neomodel import db

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature.person.repo.label import AuthorUtil, LAuthor
from knowde._feature.reference.domain import Book
from knowde._feature.reference.repo.label import BookUtil, LBook
from knowde.feature.definition.domain.domain import Definition
from knowde.feature.definition.repo.definition import RelDefUtil, add_definition
from knowde.reference.domain import RefDefinitions
from knowde.reference.dto import BookParam, RefDefParam  # noqa: TCH001

RelAuthorUtil = RelUtil(
    t_source=LAuthor,
    t_target=LBook,
    name="WRITE",
)

# RelBookRefUtil = RelUtil(
#     t_source=LBook,
#     t_target=,

#         )


def add_book_with_author(p: BookParam) -> None:
    """著者と本を追加する."""
    book = BookUtil.create(title=p.title)
    if p.author_name is not None:
        author = AuthorUtil.find_one_or_none(name=p.author_name)
        if author is None:
            author = AuthorUtil.create(name=p.author_name)
        RelAuthorUtil.connect(author.label, book.label)


def add_refdef(p: RefDefParam) -> RefDefinitions:
    """本から引用した定義を追加.

    どんな記述があったかが大事なので、Termは引用に含めないことにする
    """
    d = add_definition(p.to_defparam())
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH
            (t:Term)-[def:{dn} {{uid: $d_uid}}]->(s:Sentence),
            (r:Reference {{uid: $uid}})
        CREATE (s)-[:REFER]->(r)
        RETURN def, r
        """,
        params={
            "uid": p.ref_uid.hex,
            "d_uid": d.valid_uid.hex,
        },
    )
    return RefDefinitions(
        book=res.get("r", convert=Book.to_model)[0],
        defs=res.get("def", convert=Definition.from_rel),
    )


def list_refdefs(ref_uid: UUID) -> list[RefDefinitions]:
    """引用付き定義一覧."""
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH (t:Term)-[def:{dn}]->(s:Sentence)
            -[:REFER]->(r:Reference {{uid: $uid}})
        RETURN collect(def) as defs, r
        """,
        params={"uid": ref_uid.hex},
    )
    rds = []
    for x, y in zip(res.get("defs"), res.get("r", convert=Book.to_model), strict=True):
        rd = RefDefinitions(
            book=y,
            defs=[Definition.from_rel(rel) for rel in x[0]],
        )
        rds.append(rd)
    return rds


def add_def2ref(ref_uid: UUID, def_uids: list[UUID]) -> None:
    """本と定義を紐付ける."""
    dn = RelDefUtil.name
    query_cypher(
        f"""
        MATCH (r:Reference {{uid: $ref_uid}}),
            (t:Term)-[def:{dn} WHERE def.uid IN $def_uids]->(s:Sentence)
        CREATE (t)-[:REFER]->(r), (s)-[:REFER]->(r)
        """,
        params={
            "ref_uid": ref_uid.hex,
            "def_uids": [uid.hex for uid in def_uids],
        },
    )


def disconnect_refdef(ref_uid: UUID, def_uids: list[UUID]) -> None:
    """本と定義の紐付けを解除する.

    定義自体を削除したいのなら、definitionパッケージの機能を使えば良い
    """
    dn = RelDefUtil.name
    query_cypher(
        f"""
        MATCH (r:Reference {{uid: $ref_uid}}),
            (t:Term)-[def:{dn} WHERE def.uid IN $def_uids]->(s:Sentence)
            -[rrel:REFER]->(r)
        DELETE rrel
        """,
        params={
            "ref_uid": ref_uid.hex,
            "def_uids": [uid.hex for uid in def_uids],
        },
    )


@db.transaction
def change_def2ref(
    old_uid: UUID,
    new_uid: UUID,
    def_uids: list[UUID],
) -> None:
    """引用の紐付けを変更."""
    disconnect_refdef(old_uid, def_uids)
    add_def2ref(new_uid, def_uids)
