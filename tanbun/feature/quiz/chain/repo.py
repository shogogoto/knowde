"""QuizChainのrepo."""

from collections import defaultdict
from uuid import UUID

from neomodel import adb

from tanbun.feature.domain.types import UUIDy, to_uuid
from tanbun.feature.quiz.chain.domain import (
    QuizChain,
    QuizChainLink,
    QuizChainQuiz,
    QuizChainRole,
)
from tanbun.feature.quiz.repo.restore import (
    restore_quiz_sources_with_tanbuns,
)

RELATION_TO_ROLE = {
    "QUIZ_TARGET": QuizChainRole.TARGET,
    "QUIZ_OPTION": QuizChainRole.OPTION,
    "CORRECT": QuizChainRole.CORRECT,
}


async def fetch_quiz_chain(quiz_id: UUIDy) -> QuizChain | None:
    """Quizを起点に関連Sentenceを1ホップ取得."""
    q = """
        MATCH (quiz: Quiz {uid: $quiz_id})
        MATCH (quiz)-[relation:QUIZ_TARGET|QUIZ_OPTION|CORRECT]->(
            sentence: Sentence
        )
        RETURN
            sentence.uid,
            type(relation)
        ORDER BY sentence.uid, type(relation)
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"quiz_id": to_uuid(quiz_id).hex},
    )
    sources, knowdes = await restore_quiz_sources_with_tanbuns([quiz_id])
    if not sources:
        return None

    source = sources[0]
    options = {to_uuid(uid): option for uid, option in source.sources.items()}
    sentences = {}
    links = []
    for raw_sentence_id, relation_type in rows:
        sentence_id = to_uuid(raw_sentence_id)
        sentences[sentence_id] = knowdes[sentence_id.hex]
        links.append(
            QuizChainLink(
                quiz_id=source.quiz_id,
                sentence_id=sentence_id,
                role=RELATION_TO_ROLE[relation_type],
                relations=list(options[sentence_id].rels or []),
            ),
        )
    return QuizChain(
        sentences=list(sentences.values()),
        quizzes=[
            QuizChainQuiz(
                quiz_id=source.quiz_id,
                quiz_type=source.quiz_type,
                readable=source.to_readable(),
            ),
        ],
        links=links,
    )


async def fetch_sentence_chain(
    sentence_id: UUIDy,
    quiz_ids: list[UUIDy],
) -> QuizChain | None:
    """Sentenceを起点に指定された関連Quizを1ホップ取得."""
    q = """
        MATCH (sentence: Sentence {uid: $sentence_id})
        OPTIONAL MATCH (quiz: Quiz)-[
            relation:QUIZ_TARGET|QUIZ_OPTION|CORRECT
        ]->(sentence)
        WHERE quiz IS NULL OR quiz.uid IN $quiz_ids
        RETURN
            sentence.uid,
            quiz.uid,
            type(relation)
        ORDER BY quiz.created DESC, quiz.uid, type(relation)
    """
    rows, _ = await adb.cypher_query(
        q,
        params={
            "sentence_id": to_uuid(sentence_id).hex,
            "quiz_ids": [to_uuid(quiz_id).hex for quiz_id in quiz_ids],
        },
    )
    if not rows:
        return None

    sid, _, _ = rows[0]
    sources, knowdes = await restore_quiz_sources_with_tanbuns(
        quiz_ids,
        extra_uids=[sentence_id],
    )
    source_by_id = {source.quiz_id: source for source in sources}
    options_by_quiz = {
        source.quiz_id: {to_uuid(uid): option for uid, option in source.sources.items()}
        for source in sources
    }
    roles_by_quiz: dict[UUID, list[QuizChainRole]] = defaultdict(list)
    for _, quiz_id, relation_type in rows:
        if quiz_id is not None:
            roles_by_quiz[to_uuid(quiz_id)].append(
                RELATION_TO_ROLE[relation_type],
            )

    sid = to_uuid(sid)
    return QuizChain(
        sentences=[knowdes[sid.hex]],
        quizzes=[
            QuizChainQuiz(
                quiz_id=source.quiz_id,
                quiz_type=source.quiz_type,
                readable=source.to_readable(),
            )
            for source in sources
        ],
        links=[
            QuizChainLink(
                quiz_id=quiz_id,
                sentence_id=sid,
                role=role,
                relations=list(
                    options_by_quiz[quiz_id][sid].rels or [],
                ),
            )
            for quiz_id, roles in roles_by_quiz.items()
            if quiz_id in source_by_id
            for role in roles
        ],
    )


async def fetch_related_quiz_ids(sentence_id: UUIDy) -> list[UUID]:
    """Sentenceに直接関連するQuiz IDを取得."""
    q = """
        MATCH (quiz: Quiz)-[:QUIZ_TARGET|QUIZ_OPTION|CORRECT]->(
            :Sentence {uid: $sentence_id}
        )
        WITH DISTINCT quiz
        ORDER BY quiz.created DESC, quiz.uid ASC
        RETURN quiz.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"sentence_id": to_uuid(sentence_id).hex},
    )
    return [to_uuid(row[0]) for row in rows]
