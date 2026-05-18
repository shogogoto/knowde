"""quiz domain test.

多段関係 ex. この前提の前提はどれ
複数選択がマルになるケースにも対応する.
"""

import uuid
from datetime import datetime

import pytest

from knowde.feature.parsing.sysnet import SysNet
from knowde.integration.quiz.domain.parts import QuizRel
from knowde.integration.quiz.errors import InvalidAnswerOptionError, QuizDuplicateError
from knowde.integration.quiz.fixture import fx_sn
from knowde.shared.util import TZ

from .domain import QuizOption, QuizSource, QuizType


def test_duplicate_source():
    """重複チェック."""
    op = QuizOption.create("aaa", ["A"])
    with pytest.raises(QuizDuplicateError):
        QuizSource(
            quiz_id=uuid.uuid4(),
            quiz_type=QuizType.SENT2TERM,
            target_id="1",
            sources=dict.fromkeys(["1", "2"], op),
            created=datetime.now(tz=TZ),
        )


sn = pytest.fixture(fx_sn)


def test_sysnet2source(sn: SysNet):
    """sysnetからquizsourceへの変換(テストを書きやすくする)."""
    src = QuizSource(
        quiz_id=uuid.uuid4(),
        quiz_type=QuizType.REL2PAIR,
        target_id="1",  # 問いの対象
        correct_ids=["2"],
        sources={
            "1": QuizOption(val=sn.get("ccc"), rels=[]),
            "2": QuizOption(val=sn.get("ccc1"), rels=[QuizRel.DETAIL]),
            "3": QuizOption(val=sn.get("to"), rels=[QuizRel.CONCLUSION]),
            "4": QuizOption(val=sn.get("cccb"), rels=[QuizRel.PREMISE]),
            "5": QuizOption(val=sn.get("cccb1"), rels=[QuizRel.PREMISE] * 2),
            "6": QuizOption(val=sn.get("parent"), rels=[QuizRel.PARENT]),
        },
        created=datetime.now(tz=TZ),
    )
    qs = QuizSource.from_sysnet(
        sn=sn,
        qt=QuizType.REL2PAIR,
        target_stc="ccc",
        source_stcs=["ccc", "ccc1", "to", "cccb", "cccb1", "parent"],
        correct_stcs=["ccc1"],
    )
    assert src.quiz_type == qs.quiz_type
    assert src.target_id == qs.target_id
    assert src.correct_ids == qs.correct_ids
    assert src.sources == qs.sources


def test_quiz_sent2term(sn: SysNet):
    """用語当て問題."""
    src = QuizSource.from_sysnet(
        sn=sn,
        qt=QuizType.SENT2TERM,
        target_stc="aaa",
        source_stcs=["aaa", "bbb", "ccc", "ddd"],
    )
    q = src.to_readable()
    assert q.statement == "'aaa'に合う用語を当ててください"
    assert set(q.options.values()) == {"A", "B", "C", "D"}
    assert q.is_correct(["1"])
    assert not q.is_correct(["1", "4"])
    assert not q.is_correct(["2"])
    assert not q.is_correct(["2", "3", "4"])
    assert not q.is_correct([])
    with pytest.raises(InvalidAnswerOptionError):
        q.is_correct(["999"])


def test_quiz_term2sent(sn: SysNet):
    """単文当て問題."""
    src = QuizSource.from_sysnet(
        sn=sn,
        qt=QuizType.TERM2SENT,
        target_stc="aaa",
        source_stcs=["aaa", "bbb", "ccc", "ddd"],
    )
    q = src.to_readable()
    assert set(q.options.values()) == {"aaa", "bbb", "ccc", "ddd"}
    assert q.statement == QuizType.TERM2SENT.inject(["A"])
    assert q.is_correct(["1"])
    assert not q.is_correct(["1", "4"])
    assert not q.is_correct(["2"])
    assert not q.is_correct(["2", "3", "4"])
    assert not q.is_correct([])


def test_quiz_rel2sent_lv1(sn: SysNet):
    """クイズ対象と関係にマッチするもの当て問題(1階層)."""
    src = QuizSource.from_sysnet(
        sn=sn,
        qt=QuizType.REL2PAIR,
        target_stc="ccc",
        source_stcs=["ccc", "ccc1", "to", "cccb", "cccb1", "parent"],
        correct_stcs=["ccc1"],
    )
    # 詳細はどれか
    q = src.to_readable()
    assert q.statement == "'C: ccc'と'詳細'関係で繋がる単文を当ててください"
    assert q.is_correct(["2"])
    assert not q.is_correct(["3"])

    src2 = src.model_copy(update={"correct_ids": {"3"}})
    # 結論はどれか
    q = src2.to_readable()
    assert q.statement == "'C: ccc'と'結論'関係で繋がる単文を当ててください"
    assert q.is_correct(["3"])
    assert not q.is_correct(["2", "4"])
    assert not q.is_correct(["3", "4"])


def test_no_term_not_target_correct():
    """用語当てクイズでtargetを正解にしないパターン.

    correct_idsが空の場合はtarget_idを正解にする
    correct_idsがある場合はcorrent_idを正解にする
      ただし、用語当てなどの性質上、複数の正解
    """


def test_no_term_without_correct_option():
    """用語当てクイズで何も選択しないのが正解なパターン.

    correct_idsが空の場合はtarget_idを正解にする
    correct_idsがある場合はcorrent_idを正解にする
      ただし、用語当てなどの性質上、複数の正解
    """


#   quiz propertyにflagを持たせて、option関係を+1にするか
# allow_multiple_anwser: bool = False
# allow_no_correct_option: bool = False
