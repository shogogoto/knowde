"""定義の説明に他の定義を流用する.

定義を前提せずに成立させたい
"""
import pytest

from knowde._feature.sentence.repo.label import SentenceUtil
from knowde._feature.term import TermUtil
from knowde.feature.definition.repo.errors import UndefinedMarkedTermError

from .mark import find_marked_terms, mark_sentence, remark_sentence, remove_marks


def test_add_mark() -> None:
    """markを処理して登録."""
    t1 = TermUtil.create(value="t1").to_model()
    s1 = SentenceUtil.create(value="xx{t1}xx").to_model()
    mark_sentence(s1.valid_uid)
    assert find_marked_terms(s1.valid_uid) == [t1]

    s2 = SentenceUtil.create(value="xx{t2}xx").to_model()
    with pytest.raises(UndefinedMarkedTermError):
        mark_sentence(s2.valid_uid)

    t2 = TermUtil.create(value="t2").to_model()
    s3 = SentenceUtil.create(value="xx{t1}xx{t2}xx").to_model()
    mark_sentence(s3.valid_uid)
    assert find_marked_terms(s3.valid_uid) == [t1, t2]


def test_remove_mark() -> None:
    """markの削除."""
    t1 = TermUtil.create(value="t1").to_model()
    t2 = TermUtil.create(value="t2").to_model()
    t3 = TermUtil.create(value="t3").to_model()
    s = SentenceUtil.create(value="xx{t1}x{t2}x{t3}xx").to_model()
    mark_sentence(s.valid_uid)
    assert find_marked_terms(s.valid_uid) == [t1, t2, t3]
    remove_marks(s.valid_uid)
    assert find_marked_terms(s.valid_uid) == []


def test_change_mark() -> None:
    """markを変更する = delete insert."""
    t1 = TermUtil.create(value="t1").to_model()
    t2 = TermUtil.create(value="t2").to_model()
    s = SentenceUtil.create(value="xx{t1}x{t2}xx").to_model()
    mark_sentence(s.valid_uid)
    assert find_marked_terms(s.valid_uid) == [t1, t2]

    t3 = TermUtil.create(value="t3").to_model()
    remark_sentence(s.valid_uid, "xx{t3}")
    assert find_marked_terms(s.valid_uid) == [t3]
