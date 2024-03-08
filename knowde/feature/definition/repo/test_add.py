"""定義: 用語(Term)と説明の結合.

新規作成: {新規、既存} * {新規, 既存} の4通り
- 用語、説明両方とも新規
- 既存のsentenceに新規用語をくっつける
"""


import pytest

from knowde._feature.sentence import SentenceUtil
from knowde._feature.term.repo.label import TermUtil
from knowde.feature.definition.domain.domain import DefinitionParam
from knowde.feature.definition.repo.add import (
    add_definition,
    change_definition,
    find_definition,
)
from knowde.feature.definition.repo.errors import AlreadyDefinedError


def _p(name: str, explain: str) -> DefinitionParam:
    return DefinitionParam(name=name, explain=explain)


def test_add_definition() -> None:
    """新規作成: {新規、既存} * {新規, 既存} の4通り."""
    d1 = add_definition(_p("new_term1", "new_sentence1"))
    assert d1.term.valid_uid
    assert d1.sentence.valid_uid

    t1 = TermUtil.create(value="exists_term1").to_model()
    d2 = add_definition(_p(t1.value, "new_sentence2"))
    assert d2.term.valid_uid == t1.valid_uid

    s1 = SentenceUtil.create(value="exists_sentence1").to_model()
    d3 = add_definition(_p("new_term2", s1.value))
    assert d3.sentence.valid_uid == s1.valid_uid

    t2 = TermUtil.create(value="exists_term2").to_model()
    s2 = SentenceUtil.create(value="exists_sentence2").to_model()
    d4 = add_definition(_p(t2.value, s2.value))
    assert d4.term.valid_uid == t2.valid_uid
    assert d4.sentence.valid_uid == s2.valid_uid


def test_add_exists() -> None:
    """作成済みの定義."""
    name = "term"
    s = "sentence"
    add_definition(_p(name, s))
    with pytest.raises(AlreadyDefinedError):
        add_definition(_p(name, s))


def test_find_definition() -> None:
    """定義をIDから見つける."""
    d = add_definition(_p("new_term1", "sentence"))
    assert d == find_definition(d.term.valid_uid)


def test_change_definition() -> None:
    """既存の定義の変更.

    - 値の変更 term.value, sentence.value
    - 紐付けは変更しない
    """
    d = add_definition(_p("term1", "sentence1"))
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
