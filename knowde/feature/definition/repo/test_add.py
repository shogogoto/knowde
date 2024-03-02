"""定義: 用語(Term)と説明の結合.

新規作成: {新規、既存} * {新規, 既存} の4通り
- 用語、説明両方とも新規
- 既存のsentenceに新規用語をつける


- 普通にtermとsetencenを紐付ける

"""


from knowde._feature.sentence import s_util
from knowde._feature.term import term_util
from knowde.feature.definition.repo.add import create_definition


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
