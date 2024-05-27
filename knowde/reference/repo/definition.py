"""referenceとpersonに依存."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature.person.repo.label import AuthorUtil, LAuthor
from knowde._feature.reference.domain import Book
from knowde._feature.reference.repo.label import BookUtil, LBook
from knowde.feature.definition.domain.domain import Definition
from knowde.feature.definition.repo.definition import RelDefUtil, add_definition
from knowde.reference.domain import RefDefinitions

if TYPE_CHECKING:
    from knowde.reference.dto import BookParam, RefDefParam

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


def add_refdef(p: RefDefParam) -> tuple[Definition, Book]:
    """本から引用した定義を追加."""
    d = add_definition(p.to_defparam())
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH
            (t:Term)-[def:{dn} {{uid: $d_uid}}]->(s:Sentence),
            (r:Reference {{uid: $uid}})
        CREATE (t)-[:REFER]->(r), (s)-[:REFER]->(r)
        RETURN def, r
        """,
        params={
            "uid": p.ref_uid.hex,
            "d_uid": d.valid_uid.hex,
        },
    )
    return (
        res.get("def", convert=Definition.from_rel)[0],
        res.get("r", convert=Book.to_model)[0],
    )


def list_refdefs() -> list[RefDefinitions]:
    """引用付き定義一覧."""
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH (t:Term)-[def:{dn}]->(s:Sentence)-[:REFER]->(r:Reference)
        RETURN collect(def) as defs, r
        """,
    )
    rds = []
    for x, y in zip(res.get("defs"), res.get("r", convert=Book.to_model), strict=True):
        rd = RefDefinitions(
            book=y,
            defs=[Definition.from_rel(rel) for rel in x[0]],
        )
        rds.append(rd)
    return rds
    # for x in res.results:
    #     print(x)
    # # print(res.results)


# def connect_def2ref() -> None:
#     """本と定義を紐付ける."""


# def disconnect_def_from_ref() -> None:
#     """本と定義の紐付けを解除する."""
