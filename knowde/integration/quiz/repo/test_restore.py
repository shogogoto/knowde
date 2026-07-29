"""保存済みクイズの復元テスト."""

from types import SimpleNamespace

import networkx as nx
import pytest

from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.errors import QuizRestoreError

from .restore import nx2options


def test_term_quiz_allows_unrelated_distractor() -> None:
    """用語系の誤答肢は対象とknowledge pathで繋がっていなくてもよい."""
    graph = nx.DiGraph()
    graph.add_nodes_from(["target", "distractor"])
    knowdes = {
        "target": SimpleNamespace(sentence_or_def="target"),
        "distractor": SimpleNamespace(sentence_or_def="distractor"),
    }

    options = nx2options(
        knowdes,
        correct_ids=(),
        target_id="target",
        g=graph,
        uid2kn=knowdes,
        quiz_type=QuizType.TERM2SENT,
    )

    assert options["distractor"].rels is None


def test_relation_quiz_requires_knowledge_path() -> None:
    """関係系クイズのpath欠落は回答不能な保存データとして扱う."""
    graph = nx.DiGraph()
    graph.add_nodes_from(["target", "option"])
    knowdes = {
        "target": SimpleNamespace(sentence_or_def="target"),
        "option": SimpleNamespace(sentence_or_def="option"),
    }

    with pytest.raises(QuizRestoreError):
        nx2options(
            knowdes,
            correct_ids=("option",),
            target_id="target",
            g=graph,
            uid2kn=knowdes,
            quiz_type=QuizType.PAIR2REL,
        )


def test_rel2pair_allows_unrelated_distractor() -> None:
    """関係から単文を選ぶ誤答肢には、対象とのknowledge pathを要求しない."""
    graph = nx.DiGraph()
    graph.add_nodes_from(["target", "correct", "distractor"])
    graph.add_edge("target", "correct", type="TO")
    knowdes = {
        uid: SimpleNamespace(sentence_or_def=uid)
        for uid in ("target", "correct", "distractor")
    }

    options = nx2options(
        knowdes,
        correct_ids=("correct",),
        target_id="target",
        g=graph,
        uid2kn=knowdes,
        quiz_type=QuizType.REL2PAIR,
    )

    assert options["correct"].rels is not None
    assert options["distractor"].rels is None


def test_rel2pair_requires_knowledge_path_for_correct_option() -> None:
    """REL2PAIRの正解だけは、出題したknowledge pathを復元できる必要がある."""
    graph = nx.DiGraph()
    graph.add_nodes_from(["target", "correct"])
    knowdes = {
        uid: SimpleNamespace(sentence_or_def=uid) for uid in ("target", "correct")
    }

    with pytest.raises(QuizRestoreError):
        nx2options(
            knowdes,
            correct_ids=("correct",),
            target_id="target",
            g=graph,
            uid2kn=knowdes,
            quiz_type=QuizType.REL2PAIR,
        )
