"""定義の説明に他の定義を流用する."""


import pytest

from knowde._feature.sentence import s_util
from knowde._feature.term import term_util
from knowde.feature.definition.repo.errors import UndefinedMarkedTermError

from .mark import find_marked_terms, mark_sentence


def test_add_mark() -> None:
    """markを処理して登録."""
    t1 = term_util.create(value="t1").to_model()
    s1 = s_util.create(value="xx{t1}xx").to_model()
    mark_sentence(s1.valid_uid)
    assert find_marked_terms(s1.valid_uid) == [t1]

    s2 = s_util.create(value="xx{t2}xx").to_model()
    with pytest.raises(UndefinedMarkedTermError):
        mark_sentence(s2.valid_uid)

    t2 = term_util.create(value="t2").to_model()
    s3 = s_util.create(value="xx{t1}xx{t2}xx").to_model()
    mark_sentence(s3.valid_uid)
    assert find_marked_terms(s3.valid_uid) == [t1, t2]
