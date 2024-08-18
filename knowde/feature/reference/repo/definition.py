"""referenceとpersonに依存."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from neomodel import db

from knowde.complex.definition.domain.domain import Definition
from knowde.complex.definition.repo.definition import (
    add_definition,
    build_statsdefs,
    q_stats_def,
)
from knowde.complex.definition.repo.label import REL_DEF_LABEL
from knowde.core.label_repo.query import query_cypher
from knowde.feature.reference.domain import RefDefinition, RefDefinitions
from knowde.feature.reference.dto import RefDefParam  # noqa: TCH001
from knowde.primitive.reference.domain import Book
from knowde.primitive.reference.repo.label import (
    ReferenceUtil,
    to_refmodel,
)

# RelAuthorUtil = RelUtil(
#     t_source=LAuthor,
#     t_target=LBook,
#     name="WRITE",
# )

# RelBookRefUtil = RelUtil(
#     t_source=LBook,
#     t_target=,

#         )


# def add_book_with_author(p: BookParam) -> None:
#     """著者と本を追加する."""
#     book = BookUtil.create(title=p.title)
#     if p.author_name is not None:
#         author = AuthorUtil.find_one_or_none(name=p.author_name)
#         if author is None:
#             author = AuthorUtil.create(name=p.author_name)
#         RelAuthorUtil.connect(author.label, book.label)


def add_refdef(p: RefDefParam) -> RefDefinition:
    """本から引用した定義を追加.

    どんな記述があったかが大事なので、Termは引用に含めないことにする
    """
    d = add_definition(p.name, p.explain)
    dn = REL_DEF_LABEL
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
    return RefDefinition(
        book=res.get("r", convert=Book.to_model)[0],
        df=res.get("def", convert=Definition.from_rel)[0],
    )


def list_refdefs(ref_uid: UUID) -> RefDefinitions:
    """引用付き定義一覧."""
    ref = to_refmodel(ReferenceUtil.find_by_id(ref_uid).label)
    dn = REL_DEF_LABEL
    res = query_cypher(
        f"""
        MATCH (t:Term)-[def:{dn}]->(s:Sentence)
            -[:REFER]->(r:Reference {{uid: $uid}})
        {q_stats_def()}
        """,
        params={"uid": ref_uid.hex},
    )
    stdefs = build_statsdefs(res)
    return RefDefinitions(book=ref, defs=stdefs)


def connect_def2ref(ref_uid: UUID, def_uids: list[UUID]) -> None:
    """本と定義を紐付ける."""
    dn = REL_DEF_LABEL
    query_cypher(
        f"""
        MATCH (r:Reference {{uid: $ref_uid}}),
            (t:Term)-[def:{dn} WHERE def.uid IN $def_uids]->(s:Sentence)
        CREATE (s)-[:REFER]->(r)
        """,
        params={
            "ref_uid": ref_uid.hex,
            "def_uids": [uid.hex for uid in def_uids],
        },
    )


# 紐付けだけ解除するか 定義を削除すればよい
def disconnect_refdef(ref_uid: UUID, def_uids: list[UUID]) -> None:
    """本と定義の紐付けを解除する.

    定義自体を削除したいのなら、definitionパッケージの機能を使えば良い
    """
    dn = REL_DEF_LABEL
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
    connect_def2ref(new_uid, def_uids)
