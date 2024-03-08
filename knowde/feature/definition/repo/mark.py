"""説明文の依存関係解決."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared import RelBase, RelUtil
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.sentence import SentenceUtil
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import TermUtil
from knowde._feature.term.domain import Term
from knowde._feature.term.repo.label import LTerm
from knowde.feature.definition.domain.description import (
    Description,
    PlaceHeldDescription,
)
from knowde.feature.definition.repo.errors import UndefinedMarkedTermError

if TYPE_CHECKING:
    from uuid import UUID


rel_mark = RelUtil(
    t_source=LSentence,
    t_target=LTerm,
    name="MARK",
    t_rel=RelBase,
)

SentenceUtil  # noqa: B018
TermUtil  # noqa: B018


def mark_sentence(sentence_uid: UUID) -> PlaceHeldDescription:
    """markを解決して永続化."""
    s = SentenceUtil.find_by_id(sentence_uid)
    d = Description(value=s.to_model().value)
    for mv in d.markvalues:
        t = TermUtil.find_one_or_none(value=mv.value)
        if t is None:
            msg = f"用語'{mv.value}'は見つかりませんでした'"
            raise UndefinedMarkedTermError(msg)
        rel_mark.connect(s.label, t.label)  # 順番が必要な場合はここをいじる
    return d.placeheld


def find_marked_terms(sentence_uid: UUID) -> list[Term]:
    """文章にマークされた用語を取得."""
    res = query_cypher(
        f"""
        MATCH (s:Sentence)-[rel:{rel_mark.name}]->(t:Term)
        WHERE s.uid=$uid
        return t
        """,
        params={"uid": sentence_uid.hex},
    )
    return Term.to_models(res.get("t"))


# def remove_mark(sentence_uid: UUID) -> None:
#     res = query_cypher(
#         f"""
#         MATCH (s:Sentence)-[rel:{rel_mark.name}]->(t:Term)
#         WHERE s.uid=$uid
#         return t
#         """,
#         params={"uid": sentence_uid.hex},
#     )


# def resolve_description(d: Description) -> list[Description]:
#     """説明文にマークされた用語Termをみつける."""
#     # query_cypher(
#     #     """
#     #     (s:Term)-[rel:DEFINE]->(s:Sentence)

#     #     RETURN rel
#     #         """,
#     # )
#     retval = []
#     for mv in d.markvalues:
#         t = find_marked_term(mv)
#         d = find_definition(t.valid_uid)
#         if d is None:
#             raise Exception
#         retval.append(d)
#     return retval
