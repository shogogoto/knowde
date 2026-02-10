"""クイズ関連.

時系列順
回答が多い順
正答率が低い順など
"""

from collections.abc import Iterable

from neomodel import adb

from knowde.integration.quiz.domain.answer import Answer, Answers
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.collections import (
    ReadableQuizCollection,
    ReadableQuizResult,
)
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.cypher import Paging
from knowde.shared.types import UUIDy, to_uuid


async def _to_result(total: int, ids: list[str]) -> ReadableQuizResult:
    srcs = await restore_quiz_sources(ids)
    return ReadableQuizResult(
        data=ReadableQuizCollection(root=[build_readable(src) for src in srcs]),
        total=total,
    )


async def list_quiz_by_user_ids(
    user_uids: Iterable[UUIDy],
    paging: Paging = Paging(),
) -> ReadableQuizResult:
    """特定ユーザーのクイズを列挙する."""
    q = f"""
        UNWIND $user_uids AS user_uid
        MATCH (u: User {{uid: user_uid}})
        MATCH(quiz: Quiz)<-[:CREATE]-(u)
        // 新しい順
        ORDER BY quiz.created DESC
        WITH COLLECT(quiz.uid) as quiz_ids
        {paging.return_stmt("quiz_ids")}
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "user_uids": [to_uuid(uid).hex for uid in user_uids],
            **paging.params,
        },
    )
    return await _to_result(*rows[0])


async def list_quiz_by_sentence_ids(
    sent_uids: Iterable[UUIDy],
    paging: Paging = Paging(),
) -> ReadableQuizResult:
    """特定単文に紐づくクイズを列挙する."""
    q = f"""
        UNWIND $sent_uids AS sent_uid
        MATCH (s: Sentence {{uid: sent_uid}})
        MATCH(quiz: Quiz)-[:QUIZ_TARGET]->(s)
        // 新しい順
        ORDER BY quiz.created DESC
        WITH COLLECT(quiz.uid) as quiz_ids
        {paging.return_stmt("quiz_ids")}
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sent_uids": [to_uuid(uid).hex for uid in sent_uids],
            **paging.params,
        },
    )
    return await _to_result(*rows[0])


# クイズに関連するクイズを返す
#   回答した選択肢の単文に関するクイズを作る
async def list_quiz_by_optioned(
    quiz_uids: list[UUIDy],
    paging: Paging = Paging(),
):
    """クイズのオプションにあるクイズを列挙する.

    オプションのオプション ... みたいな関係を取るには
    """
    q = """
        MATCH (quiz: Quiz {uid: $quiz_uid})
        OPTIONAL MATCH p = SHORTEST 1 (quiz)-[:!QUIZ_OPTION|QUIZ_TARGET]-*(opt)
        RETURN
            COLLECT(opt.uid) AS options
            , COLLECT(p) AS paths
    """
    rows, _ = await adb.cypher_query(q, params={"quiz_uid": to_uuid(quiz_uids).hex})
    return await _to_result(*rows[0])


async def list_quiz_by_selected(
    quiz_uids: list[UUIDy],
    paging: Paging = Paging(),
):
    """回答で選択された対象のクイズを列挙する."""


# クイズの詳細で表示するくらいだと思う
async def list_answers(
    quiz_uids: list[UUIDy],
    user_uid: UUIDy | None = None,
) -> Answers:
    """クイズに対する回答一覧."""
    q = """
        UNWIND $quiz_uids AS qid
        // OPTIONAL MATCH (u: User {uid: $user_uid})
        MATCH (quiz: Quiz {uid: qid})
            <-[:ANSWER_OF]-(ans: Answer)
        // ユーザー情報を取得しつつ、user_uid が指定されていればフィルタリング
        MATCH (u: User)-[:ANSWER]->(ans)
        WHERE $user_uid IS NULL OR u.uid = $user_uid

        OPTIONAL MATCH (ans)-[:SELECT]->(s: Sentence)
        RETURN qid
            , ans
            , u
            , COLLECT(DISTINCT s.uid) AS selected
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_uids": [to_uuid(qid).hex for qid in quiz_uids],
            "user_uid": to_uuid(user_uid).hex if user_uid else None,
        },
    )

    # srcs = await restore_quiz_sources(quiz_uids)
    # rqs = {s.quiz_id.hex: build_readable(s) for s in srcs}
    # anss = {k: [] for k in rqs}
    ls = []
    for row in rows:
        qid, ans_, user, selected = row
        ans = Answer(
            answer_uid=ans_.get("uid"),
            quiz_uid=qid,
            selected=selected,
            who=user.get("uid"),
            is_correct=ans_.get("is_correct"),
            created=ans_.get("created"),
        )
        ls.append(ans)
    return Answers(root=ls)
