"""test."""

from pydantic import BaseModel

from .paramfunc import to_paramfunc


class OneParam(BaseModel, frozen=True):  # noqa: D101
    p1: int
    p2: int


def test_to_paramfunc() -> None:
    """Paramを引数に持つAPI用関数に変換."""

    def f1(p1: int, p2: int) -> int:  # noqa: FURB118
        return p1 + p2

    f = to_paramfunc(OneParam, f1)
    assert f(OneParam(p1=1, p2=10)) == 11  # noqa: PLR2004


def test_to_paramfunc_with_uuid() -> None:
    """Paramを引数に持つAPI用関数に変換."""

    def f1(uid: int, p1: int, p2: int) -> int:
        return uid + p1 + p2

    f = to_paramfunc(OneParam, f1, ignores=["uid"])
    assert f(100, OneParam(p1=1, p2=10)) == 111  # noqa: PLR2004
