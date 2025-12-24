"""ReadableQuizを組み立てる."""

from knowde.integration.quiz.domain.correct import (
    correct_is_specific_rels,
    correct_is_target,
)
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
        correct=src.filter_by(correct_is_target(src)),
    )


def tobe_readable_term2sent(src: QuizSource) -> ReadableQuiz:
    """用語から単文を選ぶ問題文を作成."""
    return ReadableQuiz(
        statement=QuizType.TERM2SENT.inject([str(src.tgt_def.term)]),
        options={
            src.target_id: str(src.tgt_sent),
            **{k: str(v.sentence) for k, v in src.source_defs.items()},
        },
        correct=src.filter_by(correct_is_target(src)),
    )


def tobe_readable_rel2sent(
    src: QuizSource,
    corrects: list[QuizRel],
) -> ReadableQuiz:
    """関係から単文を選ぶ問題文を作成."""
    fn = correct_is_specific_rels(src, corrects)
    return ReadableQuiz(
        statement=QuizType.REL2SENT.inject([str(src.target.val), src.target.rels_stmt]),
        options={
            **{k: str(v.val) for k, v in src.sources.items()},
        },
        correct=src.filter_by(fn),
    )


# def tobe_readable_quiz(src: QuizSource, corrects: )
