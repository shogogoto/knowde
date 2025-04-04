"""test."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .operate import (
    extract_generic_alias_type,
    extract_type,
)


class AModel(BaseModel):  # noqa: D101
    uids: list[UUID]


def test_extract_type() -> None:  # noqa: D103
    assert extract_type(str) is str
    assert extract_type(str | None) is str
    assert extract_type(Optional[str]) is str  # noqa: UP045
    assert extract_type(Optional[AModel]) is AModel  # noqa: UP045


def test_extract_alias() -> None:  # noqa: D103
    assert extract_generic_alias_type(AModel.model_fields["uids"].annotation) == UUID
