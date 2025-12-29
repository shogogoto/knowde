"""quiz domain test.

多段関係 ex. この前提の前提はどれ
複数選択がマルになるケースにも対応する.
"""

import uuid

import pytest

from knowde.feature.parsing.sysnet import SysNet
from knowde.integration.quiz.domain.build import (
    build_readable_rel2sent,
    build_readable_sent2term,
    build_readable_term2sent,
)
from knowde.integration.quiz.domain.parts import QuizRel, path2edgetypes, to_detail_rel
from knowde.integration.quiz.errors import InvalidAnswerOptionError, QuizDuplicateError
from knowde.integration.quiz.fixture import fx_sn
from knowde.shared.nxutil.edge_type import EdgeType

from .domain import (
    QuizOption,
    QuizSource,
    QuizType,
)


def test_duplicate_source():
    """重複チェック."""
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            quiz_id=uuid.uuid4().hex,
            statement_type=QuizType.SENT2TERM,
            target_id="1",
            target=QuizOption.create("aaa", ["A"]),
            sources={
                "2": QuizOption.create("aaa", ["A"]),
            },
        )
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            quiz_id=uuid.uuid4().hex,
            statement_type=QuizType.SENT2TERM,
            target_id="1",
            target=QuizOption.create("aaa", ["A"]),
            sources={
                "2": QuizOption.create("bbb", ["B"]),
                "3": QuizOption.create("bbb", ["B"]),
            },
        )


def test_quiz_sent2term():
    """用語当て問題."""
    src = QuizSource(
        quiz_id=uuid.uuid4().hex,
        statement_type=QuizType.SENT2TERM,
        target_id="1",
        target=QuizOption.create("aaa", ["A"]),
        sources={
            "2": QuizOption.create("bbb", ["B"]),
            "3": QuizOption.create("ccc", ["C"]),
            "4": QuizOption.create("ddd", ["D"]),
        },
    )
    q = build_readable_sent2term(src)
    assert set(q.options.values()) == {"A", "B", "C", "D"}
    assert q.statement == QuizType.SENT2TERM.inject(["aaa"])
    assert q.is_correct(["1"])
    assert not q.is_correct(["1", "4"])
    assert not q.is_correct(["2"])
    assert not q.is_correct(["2", "3", "4"])
    assert not q.is_correct([])
    with pytest.raises(InvalidAnswerOptionError):
        q.is_correct(["999"])


def test_quiz_term2sent():
    """単文当て問題."""
    src = QuizSource(
        quiz_id=uuid.uuid4().hex,
        statement_type=QuizType.TERM2SENT,
        target_id="1",
        target=QuizOption.create("aaa", ["A"]),
        sources={
            "2": QuizOption.create("bbb", ["B"]),
            "3": QuizOption.create("ccc", ["C"]),
            "4": QuizOption.create("ddd", ["D"]),
        },
    )

    q = build_readable_term2sent(src)
    assert set(q.options.values()) == {"aaa", "bbb", "ccc", "ddd"}
    assert q.statement == QuizType.TERM2SENT.inject(["A"])
    assert q.is_correct(["1"])
    assert not q.is_correct(["1", "4"])
    assert not q.is_correct(["2"])
    assert not q.is_correct(["2", "3", "4"])
    assert not q.is_correct([])
    with pytest.raises(InvalidAnswerOptionError):
        q.is_correct(["999"])


sn = pytest.fixture(fx_sn)


def test_quiz_rel2sent_lv1(sn: SysNet):
    """クイズ対象と関係にマッチするもの当て問題(1階層)."""
    src = QuizSource(
        quiz_id=uuid.uuid4().hex,
        statement_type=QuizType.REL2SENT,
        target_id="1",  # 問いの対象
        target=QuizOption(val=sn.get("ccc"), rels=[QuizRel.DETAIL]),
        sources={
            "2": QuizOption(val=sn.get("ccc1"), rels=[QuizRel.DETAIL]),
            "3": QuizOption(val=sn.get("to"), rels=[QuizRel.CONCLUSION]),
            "4": QuizOption(val=sn.get("cccb"), rels=[QuizRel.PREMISE]),
            "5": QuizOption(val=sn.get("cccb1"), rels=[QuizRel.PREMISE]),
            "6": QuizOption(val=sn.get("parent"), rels=[QuizRel.PARENT]),
        },
    )

    # 詳細はどれか
    q = build_readable_rel2sent(src, [QuizRel.DETAIL])
    assert q.statement == "'C: ccc'と'詳細'関係で繋がる単文を当ててください"
    assert q.is_correct(["2"])
    assert not q.is_correct(["3"])

    # 結論はどれか
    q = build_readable_rel2sent(src, [QuizRel.CONCLUSION])
    assert q.is_correct(["3"])
    assert not q.is_correct(["2", "4"])
    assert not q.is_correct(["3", "4"])
    # 前提の前提はどれか 2階関係クイズ
    # クイズ対象からの関係を表すクラスを作るか


def test_quiz_rel2sent_random(sn: SysNet):
    """関係クイズの答えを陽に設定したくない."""


def test_path2edgetypes(sn: SysNet):
    """Graph pathからedgetypeのリストを得る."""
    assert path2edgetypes(sn.g, "ccc", "ccc1") == ([EdgeType.BELOW], True)
    assert path2edgetypes(sn.g, "ccc1", "ccc") == ([EdgeType.BELOW], False)
    assert path2edgetypes(sn.g, "ccc", "parent") == ([EdgeType.BELOW], False)
    assert path2edgetypes(sn.g, "parent", "ccc") == ([EdgeType.BELOW], True)
    assert path2edgetypes(sn.g, "ccc", "ccc3") == (
        [EdgeType.BELOW, *[EdgeType.SIBLING] * 2],
        True,
    )
    assert path2edgetypes(sn.g, "ccc3", "ccc") == (
        [EdgeType.BELOW, *[EdgeType.SIBLING] * 2],
        False,
    )
    assert path2edgetypes(sn.g, "ccc", "ccc5") == ([EdgeType.TO] * 2, True)
    assert path2edgetypes(sn.g, "ccc5", "ccc") == ([EdgeType.TO] * 2, False)
    assert path2edgetypes(sn.g, "ccc", "cccb1") == ([EdgeType.TO] * 2, False)
    assert path2edgetypes(sn.g, "cccb1", "ccc") == ([EdgeType.TO] * 2, True)


def test_to_detail_rel():
    """親子関係変換."""
    # 変換しない
    assert to_detail_rel([]) == []
    assert to_detail_rel([EdgeType.SIBLING]) == [QuizRel.PEER]
    assert to_detail_rel([EdgeType.SIBLING] * 3) == [QuizRel.PEER]
    assert to_detail_rel([EdgeType.TO]) == [EdgeType.TO]

    # 複数兄弟を含めて1つに変換
    assert to_detail_rel([EdgeType.BELOW]) == [QuizRel.DETAIL]
    one = [EdgeType.BELOW, *[EdgeType.SIBLING] * 3]
    assert to_detail_rel(one) == [QuizRel.DETAIL]

    # 2つあれば2つに
    assert to_detail_rel([*one, *one]) == [QuizRel.DETAIL] * 2

    # 混じってる
    assert to_detail_rel([*one, EdgeType.TO, *one]) == [
        QuizRel.DETAIL,
        EdgeType.TO,
        QuizRel.DETAIL,
    ]


def test_edgetypes2rel():
    """関係リストからクイズ関係を得る."""
    one = [EdgeType.BELOW, *[EdgeType.SIBLING] * 3]
    # detail
    assert QuizRel.of([EdgeType.BELOW], True) == [QuizRel.DETAIL]  # noqa: FBT003
    assert QuizRel.of(one * 2, True) == [QuizRel.DETAIL, QuizRel.DETAIL]  # noqa: FBT003
    assert QuizRel.of([EdgeType.BELOW], False) == [QuizRel.PARENT]  # noqa: FBT003
    assert QuizRel.of(one * 2, False) == [QuizRel.PARENT] * 2  # noqa: FBT003
    # to
    assert QuizRel.of([EdgeType.TO, EdgeType.TO], True) == [QuizRel.CONCLUSION] * 2  # noqa: FBT003
    assert QuizRel.of([EdgeType.TO, EdgeType.TO], False) == [QuizRel.PREMISE] * 2  # noqa: FBT003
    # 混在
    assert QuizRel.of([*one, EdgeType.TO, *one], True) == [  # noqa: FBT003
        # detail to detail
        QuizRel.DETAIL,
        QuizRel.CONCLUSION,
        QuizRel.DETAIL,
    ]
    # 複雑なパターンは網羅できてなさそうだが、そんなクイズ要るか?
    # 一旦ペンディング
