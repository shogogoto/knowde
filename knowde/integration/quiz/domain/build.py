"""ReadableQuizを組み立てる."""

# srcのquiz_typeを見に行かない関数たちは誤用のリスクあり
from knowde.integration.quiz.domain.correct.correct import (
    correct_is_target,
)
from knowde.integration.quiz.domain.domain import QuizSource, ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizType


def build_readable(src: QuizSource) -> ReadableQuiz:
    """読めるクイズを作成."""
    match src.statement_type:
        case QuizType.SENT2TERM:
            return build_readable_sent2term(src)
        case QuizType.TERM2SENT:
            return build_readable_term2sent(src)
        case QuizType.REL2PAIR:
            return build_readable_rel2pair(src)
        case QuizType.PAIR2REL:
            return build_readable_pair2rel(src)
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
        correct=src.filter_by(correct_is_target(src)),
        created=src.created,
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
        correct=src.filter_by(correct_is_target(src)),
        created=src.created,
    )


def build_readable_rel2pair(src: QuizSource) -> ReadableQuiz:
    """単文と特定の関係になっている単文(ペア)を当てる問題文を作成."""
    return ReadableQuiz(
        quiz_id=src.quiz_id,
        statement=QuizType.REL2PAIR.inject(
            [
                str(src.target.val),
                *[src.sources[c].rels_stmt for c in src.correct_ids],
            ],
        ),
        options={
            **{k: str(v.val) for k, v in src.sources.items()},
        },
        correct=list(src.correct_ids),
        created=src.created,
    )


# それらしい選択肢をでっち上げる版も作るかは要検討
def build_readable_pair2rel(src: QuizSource) -> ReadableQuiz:
    """ペアから関係を当てる問題文を作成."""
    return ReadableQuiz(
        quiz_id=src.quiz_id,
        statement=QuizType.PAIR2REL.inject(
            [
                str(src.target.val),
                *[src.sources[c].sentence for c in src.correct_ids],
            ],
        ),
        # relsが空になる場合はあり得ない
        options={
            # **{k: str([r.value for r in v.rels]) for k, v in src.sources.items()},
            **{k: str(v.rels) for k, v in src.sources.items()},
        },
        correct=list(src.correct_ids),
        created=src.created,
    )
