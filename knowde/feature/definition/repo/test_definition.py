"""定義: 用語(Term)と説明の結合.

新規作成: {新規、既存} * {新規, 既存} の4通り
- 用語、説明両方とも新規
- 既存のsentenceに新規用語をくっつける
"""


import pytest
from pytest_unordered import unordered

from knowde._feature.sentence import SentenceUtil
from knowde._feature.term import TermUtil
from knowde.feature.definition.repo.mark import find_marked_terms

from .definition import (
    add_definition,
    change_definition,
    list_definitions,
    remove_definition,
)
from .errors import AlreadyDefinedError


def test_add_definition() -> None:
    """新規作成: {新規、既存} * {新規, 既存} の4通り."""
    d1 = add_definition("new_term1", "new_sentence1")
    assert d1.term.valid_uid
    assert d1.sentence.valid_uid

    t1 = TermUtil.create(value="exists_term1").to_model()
    d2 = add_definition(t1.value, "new_sentence2")
    assert d2.term.valid_uid == t1.valid_uid

    s1 = SentenceUtil.create(value="exists_sentence1").to_model()
    d3 = add_definition("new_term2", s1.value)
    assert d3.sentence.valid_uid == s1.valid_uid

    t2 = TermUtil.create(value="exists_term2").to_model()
    s2 = SentenceUtil.create(value="exists_sentence2").to_model()
    d4 = add_definition(t2.value, s2.value)
    assert d4.term.valid_uid == t2.valid_uid
    assert d4.sentence.valid_uid == s2.valid_uid


def test_add_exists() -> None:
    """作成済みの定義."""
    name = "term"
    s = "sentence"
    add_definition(name, s)
    with pytest.raises(AlreadyDefinedError):
        add_definition(name, s)


def test_find_definition() -> None:
    """定義をIDから見つける."""
    d = add_definition("new_term1", "sentence")
    assert d == list_definitions().defs[0]


def test_change_definition() -> None:
    """既存の定義の変更.

    - 値の変更 term.value, sentence.value
    - 紐付けは変更しない
    """
    d = add_definition("term1", "sentence1")
    d2 = change_definition(d, name="term2")
    assert d.created == d2.created
    assert d.updated != d2.updated
    assert d2.term.value == "term2"

    d = d2
    d3 = change_definition(d, explain="sentence2")
    assert d.created == d3.created
    assert d.updated != d3.updated
    assert d3.sentence.value == "sentence2"

    # not change
    d = d3
    d4 = change_definition(d)
    assert d.created == d4.created
    assert d.updated == d4.updated


def test_add_with_mark() -> None:
    """markを解決して定義を追加."""
    d1 = add_definition("t1", "xxx")
    d2 = add_definition("t2", "xx{t1}xx")
    assert d2.sentence.value == "xx$@xx"
    assert find_marked_terms(d2.sentence.valid_uid) == [d1.term]
    d3 = add_definition("t3", "xx{t2}xx")

    assert d3.sentence.value == "xx$@xx"
    assert find_marked_terms(d3.sentence.valid_uid) == [d2.term]


def test_remove_with_marks() -> None:
    """markも一緒に削除する."""
    d1 = add_definition("t1", "xxx")
    d2 = add_definition("t2", "xx{t1}xx")
    assert find_marked_terms(d2.sentence.valid_uid) == [d1.term]
    remove_definition(d2.valid_uid)
    assert find_marked_terms(d2.sentence.valid_uid) == []


def test_list_definitions() -> None:
    """List definitions."""
    d1 = add_definition("t1", "xxx")
    d2 = add_definition("t2", "xx{t1}xx")
    d3 = add_definition("t3", "xx{t2}xx")
    d4 = add_definition("t4", "xx{t1}x{t2}x{t3}xx")
    assert list_definitions().defs == unordered([d1, d2, d3, d4])
