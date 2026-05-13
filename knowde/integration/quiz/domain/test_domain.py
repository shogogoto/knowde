"""quiz domain test.

多段関係 ex. この前提の前提はどれ
複数選択がマルになるケースにも対応する.
"""

import uuid
from datetime import datetime

import pytest

from knowde.feature.parsing.sysnet import SysNet
from knowde.integration.quiz.domain.parts import QuizRel, to_detail_rel
from knowde.integration.quiz.errors import InvalidAnswerOptionError, QuizDuplicateError
from knowde.integration.quiz.fixture import fx_sn
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.util import TZ

from .domain import QuizOption, QuizSource, QuizType


def test_duplicate_source():
    """重複チェック."""
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            quiz_id=uuid.uuid4(),
            quiz_type=QuizType.SENT2TERM,
            target_id="1",
            sources={
                "1": QuizOption.create("aaa", ["A"]),
                "2": QuizOption.create("aaa", ["A"]),
            },
            created=datetime.now(tz=TZ),
        )
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            quiz_id=uuid.uuid4(),
            quiz_type=QuizType.SENT2TERM,
            target_id="1",
            sources={
                "1": QuizOption.create("aaa", ["A"]),
                "2": QuizOption.create("bbb", ["B"]),
                "3": QuizOption.create("bbb", ["B"]),
            },
            created=datetime.now(tz=TZ),
        )


def test_quiz_sent2term():
    """用語当て問題."""
    src = QuizSource(
        quiz_id=uuid.uuid4(),
        quiz_type=QuizType.SENT2TERM,
        target_id="1",
        sources={
            "1": QuizOption.create("aaa", ["A"]),
            "2": QuizOption.create("bbb", ["B"]),
            "3": QuizOption.create("ccc", ["C"]),
            "4": QuizOption.create("ddd", ["D"]),
        },
        created=datetime.now(tz=TZ),
    )
    q = src.to_readable()
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
        quiz_id=uuid.uuid4(),
        quiz_type=QuizType.TERM2SENT,
        target_id="1",
        sources={
            "1": QuizOption.create("aaa", ["A"]),
            "2": QuizOption.create("bbb", ["B"]),
            "3": QuizOption.create("ccc", ["C"]),
            "4": QuizOption.create("ddd", ["D"]),
        },
        created=datetime.now(tz=TZ),
    )

    q = src.to_readable()
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
        quiz_id=uuid.uuid4(),
        quiz_type=QuizType.REL2PAIR,
        target_id="1",  # 問いの対象
        correct_ids=["2"],
        sources={
            "1": QuizOption(val=sn.get("ccc"), rels=[QuizRel.DETAIL]),
            "2": QuizOption(val=sn.get("ccc1"), rels=[QuizRel.DETAIL]),
            "3": QuizOption(val=sn.get("to"), rels=[QuizRel.CONCLUSION]),
            "4": QuizOption(val=sn.get("cccb"), rels=[QuizRel.PREMISE]),
            "5": QuizOption(val=sn.get("cccb1"), rels=[QuizRel.PREMISE]),
            "6": QuizOption(val=sn.get("parent"), rels=[QuizRel.PARENT]),
        },
        created=datetime.now(tz=TZ),
    )

    # 詳細はどれか
    q = src.to_readable()
    assert q.statement == "'C: ccc'と'詳細'関係で繋がる単文を当ててください"
    assert q.is_correct(["2"])
    assert not q.is_correct(["3"])

    src2 = src.model_copy(update={"correct_ids": {"3"}})
    # 結論はどれか
    q = src2.to_readable()
    assert q.is_correct(["3"])
    assert not q.is_correct(["2", "4"])
    assert not q.is_correct(["3", "4"])
    # 前提の前提はどれか 2階関係クイズ
    # クイズ対象からの関係を表すクラスを作るか


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
