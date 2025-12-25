"""ReadableQuizを組み立てる."""

from knowde.integration.quiz.domain.correct import (
    correct_specific_rels,
    correct_target,
)
from knowde.integration.quiz.domain.domain import QuizSource, ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizRel, QuizType


def build_readable(src: QuizSource) -> ReadableQuiz:
    """読めるクイズを作成."""
    match src.statement_type:
        case QuizType.SENT2TERM:
            return build_readable_sent2term(src)
        case QuizType.TERM2SENT:
            return build_readable_term2sent(src)
        # case QuizType.REL2SENT:
        #     return tobe_readable_rel2sent(
        #         src,
        #         src.filter_by(correct_is_target(src))
        #     )
        case _:
            msg = f"unknown statement type: {src.statement_type}"
            raise ValueError(msg)


def build_readable_sent2term(src: QuizSource) -> ReadableQuiz:
    """単文から用語を選ぶ問題文を作成."""
    return ReadableQuiz(
        quiz_id=src.quiz_id,
        statement=QuizType.SENT2TERM.inject([src.tgt_sent]),
        options={
            src.target_id: str(src.tgt_def.term),
            **{k: str(v.term) for k, v in src.source_defs.items()},
        },
        correct=src.filter_by(correct_target(src)),
    )


def build_readable_term2sent(src: QuizSource) -> ReadableQuiz:
    """用語から単文を選ぶ問題文を作成."""
    return ReadableQuiz(
        quiz_id=src.quiz_id,
        statement=QuizType.TERM2SENT.inject([str(src.tgt_def.term)]),
        options={
            src.target_id: str(src.tgt_sent),
            **{k: str(v.sentence) for k, v in src.source_defs.items()},
        },
        correct=src.filter_by(correct_target(src)),
    )


def build_readable_rel2sent(
    src: QuizSource,
    corrects: list[QuizRel],
) -> ReadableQuiz:
    """関係から単文を選ぶ問題文を作成."""
    return ReadableQuiz(
        quiz_id=src.quiz_id,
        statement=QuizType.REL2SENT.inject([str(src.target.val), src.target.rels_stmt]),
        options={
            **{k: str(v.val) for k, v in src.sources.items()},
        },
        correct=src.filter_by(correct_specific_rels(src, corrects)),
    )
