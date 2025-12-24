"""ReadableQuizを組み立てる."""

from knowde.integration.quiz.domain.domain import QuizSource, ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizRel, QuizType


def tobe_readable_sent2term(src: QuizSource) -> ReadableQuiz:
    """単文から用語を選ぶ問題文を作成."""
    return ReadableQuiz(
        statement=QuizType.SENT2TERM.inject([src.tgt_sent]),
        options={
            src.target_id: str(src.tgt_def.term),
            **{k: str(v.term) for k, v in src.source_defs.items()},
        },
        correct=[src.target_id],
    )


def tobe_readable_term2sent(src: QuizSource) -> ReadableQuiz:
    """用語から単文を選ぶ問題文を作成."""
    return ReadableQuiz(
        statement=QuizType.TERM2SENT.inject([str(src.tgt_def.term)]),
        options={
            src.target_id: str(src.tgt_sent),
            **{k: str(v.sentence) for k, v in src.source_defs.items()},
        },
        correct=[src.target_id],
    )


def tobe_readable_rel2sent(
    src: QuizSource,
    corrent_rels: list[QuizRel],
) -> ReadableQuiz:
    """関係から単文を選ぶ問題文を作成."""
    rels = src.target.rels
    if rels is None:
        raise ValueError

    rels_stmt = "の".join([str(r) for r in rels])
    correct_ids = [
        k
        for k, v in src.sources.items()
        if v.rels == corrent_rels and k != src.target_id  # 自信は選択肢になり得ない
    ]
    return ReadableQuiz(
        statement=QuizType.REL2SENT.inject([str(src.target.val), rels_stmt]),
        options={
            **{k: str(v.val) for k, v in src.sources.items()},
        },
        correct=correct_ids,
    )
