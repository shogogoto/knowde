"""reference domain model."""
from __future__ import annotations

from pydantic import BaseModel


class BookParam(BaseModel, frozen=True):
    """本作成パラメータ."""

    title: str
    author_name: str | None = None
