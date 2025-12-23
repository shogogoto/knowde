"""quiz domain test.

多段関係 ex. この前提の前提はどれ
複数選択がマルになるケースにも対応する.
"""

import pytest

from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.integration.quiz.domain.build import (
    create_quiz_edge2sent,
    create_quiz_sent2term,
    create_quiz_term2sent,
)
from knowde.integration.quiz.domain.parts import QuizRel, path2edgetypes, to_detail_rel
from knowde.integration.quiz.errors import AnswerError, QuizDuplicateError
from knowde.shared.nxutil.edge_type import EdgeType

from .domain import (
    QuizOption,
    QuizSource,
    QuizStatementType,
)


def test_duplicate_source():
    """重複チェック."""
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            statement_type=QuizStatementType.SENT2TERM,
            target_id="1",
            target=QuizOption.create("aaa", ["A"]),
            sources={
                "2": QuizOption.create("aaa", ["A"]),
            },
        )
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            statement_type=QuizStatementType.SENT2TERM,
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
        statement_type=QuizStatementType.SENT2TERM,
        target_id="1",
        target=QuizOption.create("aaa", ["A"]),
        sources={
            "2": QuizOption.create("bbb", ["B"]),
            "3": QuizOption.create("ccc", ["C"]),
            "4": QuizOption.create("ddd", ["D"]),
        },
    )
    q = create_quiz_sent2term(src, "q001")
    assert set(q.options.values()) == {"A", "B", "C", "D"}
    assert q.statement == QuizStatementType.SENT2TERM.inject(["aaa"])
    ans0 = q.answer(["1"])
    ans1 = q.answer(["1", "4"])
    ans2 = q.answer(["2"])
    ans3 = q.answer(["2", "3", "4"])
    ans4 = q.answer([])
    with pytest.raises(AnswerError):
        q.answer(["999"])

    assert ans0.is_corrent()
    assert not ans1.is_corrent()
    assert not ans2.is_corrent()
    assert not ans3.is_corrent()
    assert not ans4.is_corrent()


def test_quiz_term2sent():
    """単文当て問題."""
    src = QuizSource(
        statement_type=QuizStatementType.TERM2SENT,
        target_id="1",
        target=QuizOption.create("aaa", ["A"]),
        sources={
            "2": QuizOption.create("bbb", ["B"]),
            "3": QuizOption.create("ccc", ["C"]),
            "4": QuizOption.create("ddd", ["D"]),
        },
    )

    q = create_quiz_term2sent(src, "q001")
    assert set(q.options.values()) == {"aaa", "bbb", "ccc", "ddd"}
    assert q.statement == QuizStatementType.TERM2SENT.inject(["A"])
    ans0 = q.answer(["1"])
    ans1 = q.answer(["1", "4"])
    ans2 = q.answer(["2"])
    ans3 = q.answer(["2", "3", "4"])
    ans4 = q.answer([])
    with pytest.raises(AnswerError):
        q.answer(["999"])

    assert ans0.is_corrent()
    assert not ans1.is_corrent()
    assert not ans2.is_corrent()
    assert not ans3.is_corrent()
    assert not ans4.is_corrent()


@pytest.fixture()
def sn() -> SysNet:  # noqa: D103
    s = """
        # title
            aaa
            bbb
            parent
                C: ccc
                    T1: ccc1
                    T2: ccc2
                    T3: ccc3
                    -> to
                        T4: todetail
                        -> ccc5
                    <- cccb
                        <- cccb1
    """
    return parse2net(s)


def test_quiz_edge2sent_lv1(sn: SysNet):
    """クイズ対象と関係にマッチするもの当て問題(1階層)."""
    src = QuizSource(
        statement_type=QuizStatementType.EDGE2SENT,
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
    q = create_quiz_edge2sent(src, "q001", [QuizRel.DETAIL])
    assert q.statement == "'C: ccc'と'詳細'関係で繋がる単文を当ててください"
    assert q.answer(["2"]).is_corrent()
    assert not q.answer(["3"]).is_corrent()

    # 結論はどれか
    q = create_quiz_edge2sent(src, "q002", [QuizRel.CONCLUSION])
    assert q.answer(["3"]).is_corrent()
    assert not q.answer(["2", "4"]).is_corrent()
    assert not q.answer(["3", "4"]).is_corrent()
    # 前提の前提はどれか 2階関係クイズ
    # クイズ対象からの関係を表すクラスを作るか


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
