"""定義の説明に他の定義を流用する.

定義を前提せずに成立させたい
"""
import pytest

from knowde._feature.term import TermUtil
from knowde.feature.definition.domain.description import Description
from knowde.feature.definition.repo.errors import UndefinedMarkedTermError

from .mark import add_description, find_marked_terms, remark_sentence, remove_marks


def test_add_mark() -> None:
    """markを処理して登録."""
    t1 = TermUtil.create(value="t1").to_model()
    s1 = add_description(Description(value="xx{t1}xx")).to_model()
    assert find_marked_terms(s1.valid_uid) == [t1]

    with pytest.raises(UndefinedMarkedTermError):
        add_description(Description(value="xx{t2}xx"))

    t2 = TermUtil.create(value="t2").to_model()
    s3 = add_description(Description(value="xx{t1}xx{t2}xx")).to_model()
    assert find_marked_terms(s3.valid_uid) == [t1, t2]


def test_remove_mark() -> None:
    """markの削除."""
    t1 = TermUtil.create(value="t1").to_model()
    t2 = TermUtil.create(value="t2").to_model()
    t3 = TermUtil.create(value="t3").to_model()
    s = add_description(Description(value="xx{t1}x{t2}x{t3}xx")).to_model()
    assert s.value == "xx$@x$@x$@xx"
    assert find_marked_terms(s.valid_uid) == [t1, t2, t3]
    s = remove_marks(s.valid_uid).to_model()
    assert find_marked_terms(s.valid_uid) == []
    assert s.value == "xxt1xt2xt3xx"


def test_change_mark() -> None:
    """markを変更する = delete insert."""
    t1 = TermUtil.create(value="t1").to_model()
    t2 = TermUtil.create(value="t2").to_model()
    s = add_description(Description(value="xx{t1}x{t2}xx")).to_model()
    assert find_marked_terms(s.valid_uid) == [t1, t2]

    t3 = TermUtil.create(value="t3").to_model()
    s2 = remark_sentence(s.valid_uid, Description(value="xx{t3}xx")).to_model()
    assert s2.value == "xx$@xx"
    assert find_marked_terms(s2.valid_uid) == [t3]
