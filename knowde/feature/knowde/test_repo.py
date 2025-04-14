"""test.

誰でも見れる


register user
knowde search


sync
"""

import pytest
from pytest_unordered import unordered

from knowde.feature.knowde.repo import save_text, search_knowde
from knowde.primitive.user.repo import LUser


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="one@gmail.com").save()


def test_get_knowde_attrs(u: LUser):
    """文の所属などを取得."""
    s = """
    # title1
        @author John Due
        @published H20/11/1
    ## xxx
        A, A1, A2: a
            when. 20C
            -> P: aaa
            aaaa
        B: bA123
        A11, TNTN: ちん
        D: bbbaaaaa
    """
    save_text(u.uid, s)
    adjs = search_knowde("A1")
    # for adj in adjs:
    #     print("-" * 30)
    #     print(adj)
    #     # print(adj.model_dump_json(indent=2))
    assert [a.center.sentence for a in adjs] == unordered(["a", "ちん", "bA123"])
