"""test."""
from __future__ import annotations

from inspect import signature
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from .func import (
    MappingField2ArgumentError,
    VariadicArgumentsUndefinedError,
    check_map_fields2params,
    eq_fieldparam_type,
    rename_argument,
)

if TYPE_CHECKING:
    from datetime import date, datetime
    from uuid import UUID


def test_rename_argument() -> None:
    """Valid case."""

    def func(
        a: str,
        b: int,
        *args,
        **kwargs,
    ) -> tuple[str, int]:
        return a, b

    func2 = rename_argument("a", "replaced")(func)
    arg1, arg2 = "xyz", 1
    assert "replaced" not in str(signature(func))
    assert func(arg1, arg2) == func2(arg1, arg2)
    assert "replaced" in str(signature(func2))


def test_invalid_rename_argument() -> None:
    """Invalid case."""
    with pytest.raises(VariadicArgumentsUndefinedError):

        @rename_argument("a", "replaced")
        def func(a: str, b: int) -> tuple[str, int]:
            # def func(a: str, b: int) -> tuple[str, int]:
            return a, b


def test_eq_fieldparam_type() -> None:
    """引数とfieldのannotationを比較."""

    class InnerParam(BaseModel, frozen=True):
        p1: str
        p2: int

    class Param(BaseModel, frozen=True):
        p1: str
        p2: bool
        p3: int
        p4: float
        p5: date
        p6: datetime
        p7: UUID
        p8: InnerParam
        p9: list[UUID]

    def f(
        p1: str,
        p2: bool,  # noqa: FBT001
        p3: int,
        p4: float,
        p5: date,
        p6: datetime,
        p7: UUID,
        p8: InnerParam,
        p9: list[UUID],
    ) -> None:
        pass

    fields = Param.model_fields
    for k, p in signature(f).parameters.items():
        ft = fields[k]
        assert eq_fieldparam_type(p, ft)


def test_extra_map() -> None:
    """引数とfieldの数が一致しない."""

    class OneParam(BaseModel, frozen=True):
        p1: str
        p2: int

    def f1(p1: str) -> None:
        pass

    with pytest.raises(MappingField2ArgumentError):
        check_map_fields2params(OneParam, signature(f1).parameters)

    def f2(p1: str, p2: int, p3: float) -> None:
        pass

    with pytest.raises(MappingField2ArgumentError):
        check_map_fields2params(OneParam, signature(f2).parameters)


def test_filedarg_diff_type() -> None:
    """引数とfieldの型が一致しない."""

    class OneParam(BaseModel, frozen=True):
        p1: str
        p2: int

    def f1(p1: str, p2: float) -> None:
        pass

    with pytest.raises(MappingField2ArgumentError):
        check_map_fields2params(OneParam, signature(f1).parameters)


def test_fieldarg_default() -> None:
    """引数とfieldのデフォルト値が異なる."""

    class OneParam(BaseModel, frozen=True):
        p1: str = "xxx"
        p2: int = 0

    def f1(p1: str = "xxx", p2: int = 1) -> None:
        pass

    with pytest.raises(MappingField2ArgumentError):
        check_map_fields2params(OneParam, signature(f1).parameters)
