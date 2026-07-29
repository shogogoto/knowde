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
        "target",
        graph,
        knowdes,
        QuizType.TERM2SENT,
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
            "target",
            graph,
            knowdes,
            QuizType.PAIR2REL,
        )
