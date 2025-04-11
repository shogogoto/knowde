"""test.

誰でも見れる


register user
knowde search


sync
"""

import pytest

from knowde.primitive.user.repo import LUser


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="one@gmail.com").save()


def test_get_knowde_attrs():
    """文の所属などを取得."""


def test_x():
    """Aaa."""


# def test_aaaa(u: LUser):
#     """Test."""
#     repo = NameSpaceRepo(user=u)
#     with repo.ns_scope() as ns:
#         f11 = repo.add_folders("f1", "f11")
#         f12 = repo.add_folders("f1", "f12")
#         f21 = repo.add_folders("f2", "f21")
#         f3 = repo.add_folders("f3")

#         nxprint(ns.g)
#         s1 = """
#         # r1
#             @author aaa
#         """
#         print(txt2meta(s1))
#         # r1 = f11.write_resource(s1)
