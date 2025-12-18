"""quiz 組み立て."""

from knowde.integration.quiz.domain.domain import QuizSource, ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizRel


def create_quiz_sent2term(src: QuizSource, quiz_id: str) -> ReadableQuiz:
    """単文から用語を選ぶ問題文を作成."""
    t = src.statement_type
    return ReadableQuiz(
        uid=quiz_id,
        statement=t.inject([src.tgt_sent]),
        # 選択肢に正解を含めるとは限らないケース
        options=src.term_options(),
        correct=[src.target_id],
    )


def create_quiz_term2sent(src: QuizSource, quiz_id: str) -> ReadableQuiz:
    """用語から単文を選ぶ問題文を作成."""
    t = src.statement_type
    return ReadableQuiz(
        uid=quiz_id,
        statement=t.inject([str(src.tgt_def.term)]),
        options=src.sentence_options(),
        correct=[src.target_id],
    )


def create_quiz_edge2str(
    src: QuizSource,
    quiz_id: str,
    corrent_rel: QuizRel,
) -> ReadableQuiz:
    """関係から単文を選ぶ問題文を作成."""
    t = src.statement_type
    rel = src.tgt.rel
    if rel is None:
        raise ValueError
    correct_ids = [
        k
        for k, v in src.sources.items()
        if v.rel == corrent_rel and k != src.target_id  # 自信は選択肢になり得ない
    ]
    return ReadableQuiz(
        uid=quiz_id,
        statement=t.inject([str(src.tgt.val), rel]),
        options={
            **{k: str(src.sources[k].val) for k in correct_ids},
            **{k: str(v.val) for k, v in src.distractors.items()},
        },
        correct=correct_ids,
    )
