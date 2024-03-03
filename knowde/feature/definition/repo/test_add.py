"""定義: 用語(Term)と説明の結合.

新規作成: {新規、既存} * {新規, 既存} の4通り
- 用語、説明両方とも新規
- 既存のsentenceに新規用語をつける


- 普通にtermとsetencenを紐付ける

"""


import pytest

from knowde._feature.sentence import s_util
from knowde._feature.term import term_util
from knowde.feature.definition.repo.add import (
    create_definition,
    find_definition,
)
from knowde.feature.definition.repo.errors import AlreadyDefinedError


def test_add_definition() -> None:
    """新規作成: {新規、既存} * {新規, 既存} の4通り."""
    d1 = create_definition("new_term1", "new_sentence1")
    assert d1.term.valid_uid
    assert d1.sentence.valid_uid

    t1 = term_util.create(value="exists_term1").to_model()
    d2 = create_definition(t1.value, "new_sentence2")
    assert d2.term.valid_uid == t1.valid_uid

    s1 = s_util.create(value="exists_sentence1").to_model()
    d3 = create_definition("new_term2", s1.value)
    assert d3.sentence.valid_uid == s1.valid_uid

    t2 = term_util.create(value="exists_term2").to_model()
    s2 = s_util.create(value="exists_sentence2").to_model()
    d4 = create_definition(t2.value, s2.value)
    assert d4.term.valid_uid == t2.valid_uid
    assert d4.sentence.valid_uid == s2.valid_uid


def test_add_exists() -> None:
    """作成済みの定義."""
    name = "term"
    s = "sentence"
    create_definition(name, s)
    with pytest.raises(AlreadyDefinedError):
        create_definition(name, s)


def test_find_definition() -> None:
    """定義をIDから見つける."""
    d = create_definition("new_term1", "sentence")
    assert d == find_definition(d.term.valid_uid)


# def test_change_definition() -> None:
#     """既存の定義の変更.

#     - 値の変更 term.value, sentence.value
#     - 紐付けを変更
#     """
#     d = create_definition("term1", "sentence1")
#     t1 = term_util.create(value="term2").to_model()

#     d2 = change_definition(d, name="term2")
#     assert d.created == d2.created
#     assert d.updated != d2.updated
