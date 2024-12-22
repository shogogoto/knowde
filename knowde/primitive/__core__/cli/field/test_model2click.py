"""test."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TCH003

import click
from pydantic import BaseModel, Field
from pydantic_partial.partial import create_partial_model

from .model2click import (
    ClickParam,
    model2decorator,
    to_clickparam,
)

if TYPE_CHECKING:
    from knowde.primitive.__core__.cli.to_click import ClickDecorator


class NestedModel(BaseModel):  # noqa: D101
    nint1_1: int | None
    nint1_2: int | None
    nstr2: str
    nstr3: str


def test_to_click_param() -> None:  # noqa: D103
    class OneModel(BaseModel):
        pstr: str
        pfloat: float
        puid: UUID
        pint: int
        pbool: bool
        nested: NestedModel
        ex: str = Field(exclude=True)

    OneModelPartial = create_partial_model(OneModel)  # noqa: N806

    def _to_param(f: ClickParam) -> click.Parameter:
        @f
        def _dummy() -> None:
            pass

        return _dummy.__click_params__[0]

    p1 = _to_param(to_clickparam("_", OneModel.model_fields["pstr"]))
    p2 = _to_param(to_clickparam("_", OneModelPartial.model_fields["pstr"]))
    assert (p1.type, p1.param_type_name) == (click.STRING, "argument")
    assert (p2.type, p2.param_type_name) == (click.STRING, "option")


def _info(deco: ClickDecorator) -> list[tuple[str, str]]:
    @deco
    def _dummy() -> None:
        pass

    return [(p.name, p.param_type_name) for p in reversed(_dummy.__click_params__)]


def test_params_order() -> None:  # noqa: D103
    class ParentModel(BaseModel):
        p1_1: str | None
        p1_2: str | None
        p2: str
        p3: str
        nested: NestedModel

    class ParentModel2(BaseModel):
        p1_1: str | None
        p1_2: str | None
        nested: NestedModel
        p2: str
        p3: str

    deco = model2decorator(ParentModel)
    assert _info(deco) == [
        ("p1_1", "option"),
        ("p1_2", "option"),
        ("p2", "argument"),
        ("p3", "argument"),
        ("nint1_1", "option"),
        ("nint1_2", "option"),
        ("nstr2", "argument"),
        ("nstr3", "argument"),
    ]

    deco2 = model2decorator(ParentModel2)
    assert _info(deco2) == [
        ("p1_1", "option"),
        ("p1_2", "option"),
        ("nint1_1", "option"),
        ("nint1_2", "option"),
        ("nstr2", "argument"),
        ("nstr3", "argument"),
        ("p2", "argument"),
        ("p3", "argument"),
    ]


def test_optional_nested() -> None:  # noqa: D103
    class ParentModel3(BaseModel):
        nested: NestedModel | None
        p1_1: str | None
        p1_2: str | None
        p2: str
        p3: str

    deco = model2decorator(ParentModel3)
    assert _info(deco) == [
        ("nint1_1", "option"),
        ("nint1_2", "option"),
        ("nstr2", "option"),
        ("nstr3", "option"),
        ("p1_1", "option"),
        ("p1_2", "option"),
        ("p2", "argument"),
        ("p3", "argument"),
    ]


class WithAlias(BaseModel):  # noqa: D101
    p1: list[UUID]


def test_alias_field() -> None:
    """list[UUID]などのGenericAliasの変換."""
    deco = model2decorator(WithAlias)

    @deco
    def _f() -> None:
        pass

    arg: click.Argument = _f.__click_params__[0]
    assert arg.type == click.UUID
    assert arg.nargs == -1
