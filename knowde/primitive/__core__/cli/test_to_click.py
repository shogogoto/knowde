"""annotationをclick.ParamTypeへ変換."""

from __future__ import annotations

from uuid import UUID

import click
import pytest
from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model

from knowde.primitive.__core__.cli.to_click import to_clicktype


class NestedModel(BaseModel):  # noqa: D101
    nint1_1: int | None
    nint1_2: int | None
    nstr2: str
    nstr3: str


class OneModel(BaseModel):  # noqa: D101
    pstr: str
    pfloat: float
    puid: UUID
    pint: int
    pbool: bool
    nested: NestedModel


OneModelPartial = create_partial_model(OneModel)


def test_to_clicktype() -> None:  # noqa: D103
    assert to_clicktype(str) == click.STRING
    assert to_clicktype(int) == click.INT
    assert to_clicktype(float) == click.FLOAT
    assert to_clicktype(bool) == click.BOOL
    assert to_clicktype(UUID) == click.UUID
    with pytest.raises(TypeError):
        to_clicktype(BaseModel)
