"""quiz 組み立て."""

from knowde.integration.quiz.domain.domain import Quiz, QuizSource


def create_quiz_sent2term(src: QuizSource, quiz_id: str) -> Quiz:
    """単文から用語を選ぶ問題文を作成."""
    t = src.statement_type
    return Quiz(
        uid=quiz_id,
        statement=t.inject([src.tgt_sent]),
        # 選択肢に正解を含めるとは限らないケース
        options={
            src.target_id: str(src.tgt_def.term),
            **{k: str(v.term) for k, v in src.distractor_defs.items()},
        },
        correct=[src.target_id],
    )


def create_quiz_term2sent(src: QuizSource, quiz_id: str) -> Quiz:
    """用語から単文を選ぶ問題文を作成."""
    t = src.statement_type
    return Quiz(
        uid=quiz_id,
        statement=t.inject([str(src.tgt_def.term)]),
        # 選択肢に正解を含めるとは限らないケース
        options={
            src.target_id: str(src.tgt_sent),
            **{k: str(v.sentence) for k, v in src.distractor_defs.items()},
        },
        correct=[src.target_id],
    )


def create_quiz_edge2sent(src: QuizSource, quiz_id: str) -> Quiz:
    """関係から単文を選ぶ問題文を作成."""
    t = src.statement_type
    return Quiz(
        uid=quiz_id,
        statement=t.inject([str(src.tgt_def.term)]),
        # 選択肢に正解を含めるとは限らないケース
        options={
            src.target_id: str(src.tgt_sent),
            **{k: str(v.sentence) for k, v in src.distractor_defs.items()},
        },
        correct=[src.target_id],
    )
