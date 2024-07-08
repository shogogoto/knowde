from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .operate import (
    extract_generic_alias_type,
    extract_type,
)


class AModel(BaseModel):
    uids: list[UUID]


def test_extract_type() -> None:
    assert extract_type(str) == str
    assert extract_type(str | None) == str
    assert extract_type(Optional[str]) == str
    assert extract_type(Optional[AModel]) == AModel


def test_extract_alias() -> None:
    assert extract_generic_alias_type(AModel.model_fields["uids"].annotation) == UUID
