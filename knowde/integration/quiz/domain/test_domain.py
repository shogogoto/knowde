"""quiz domain test.

この単文の用語はどれ
この用語の説明はどれ


きめ細かい問題
この詳細はどれ 1つ正解
この親はどれ 1つ正解
この前提はどれ 2つ正解


# 多段関係
この前提の前提はどれ

複数選択がマルになるケースにも対応する


流れ
クイズ作成
問題文を見て答える Answer

全然進まん
TDDを意識すべし
クイズの具体例を列挙してテストケースへ
その実現方法を考える方向でブレークダウン
その中で適宜細かいテストを作成する

"""

import pytest

from knowde.feature.parsing.tree2net import parse2net
from knowde.integration.quiz.domain.build import (
    create_quiz_edge2str,
    create_quiz_sent2term,
    create_quiz_term2sent,
)
from knowde.integration.quiz.domain.parts import QuizRel
from knowde.integration.quiz.errors import AnswerError, QuizDuplicateError

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


def test_quiz_edge2sent_lv1():
    """クイズ対象と関係にマッチするもの当て問題(1階層)."""
    s = """
        # title
            aaa
            bbb
            parent
                C: ccc
                    Detail1: ccc1
                    Detail2: ccc2
                    Detail3: ccc3
                    -> to
                        T1: todetail
                        -> ccc5
                    <- cccA
                    <- cccB
                        <- cccB1
    """
    sn = parse2net(s)
    src = QuizSource(
        statement_type=QuizStatementType.EDGE2SENT,
        target_id="1",  # 問いの対象
        target=QuizOption(val=sn.get("ccc"), rel=QuizRel.DETAIL),
        sources={
            "2": QuizOption(val=sn.get("ccc1"), rel=QuizRel.DETAIL),
            "3": QuizOption(val=sn.get("to"), rel=QuizRel.CONCLUSION),
            "4": QuizOption(val=sn.get("cccA"), rel=QuizRel.PREMISE),
            "5": QuizOption(val=sn.get("cccB"), rel=QuizRel.PREMISE),
            "6": QuizOption(val=sn.get("parent"), rel=QuizRel.PARENT),
        },
    )

    # 詳細はどれか
    q = create_quiz_edge2str(src, "q001", QuizRel.DETAIL)
    assert q.statement == "'C: ccc'と'詳細'関係で繋がる単文を当ててください"
    assert q.answer(["2"]).is_corrent()
    assert not q.answer(["3"]).is_corrent()

    # 結論はどれか
    q = create_quiz_edge2str(src, "q002", QuizRel.CONCLUSION)
    assert q.answer(["3"]).is_corrent()
    assert not q.answer(["2", "4"]).is_corrent()
    # 前提の前提はどれか 2階関係クイズ
    # クイズ対象からの関係を表すクラスを作るか
