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

from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.integration.quiz.errors import AnswerError

from .domain import (
    QuizSource,
    QuizStatementType,
    create_quiz_sent2term,
)


def test_quiz_statement():
    """問題文の生成."""
    # 単文→用語当て
    src = QuizSource(
        statement_type=QuizStatementType.SENT2TERM,
        target_id="1",
        distractor_ids=["2", "3", "4"],
        uids={
            "1": Def.create("aaa", ["A"]),
            "2": Def.create("bbb", ["B"]),
            "3": Def.create("ccc", ["C"]),
            "4": Def.create("ddd", ["D"]),
        },
    )

    q = create_quiz_sent2term(src, "q001")
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
