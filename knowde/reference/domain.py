"""reference domain model."""
from __future__ import annotations

from pydantic import BaseModel

from knowde._feature.reference.domain import Book  # noqa: TCH001
from knowde.feature.definition.domain.domain import Definition  # noqa: TCH001


class RefDefinitions(BaseModel, frozen=True):
    """引用付き定義."""

    book: Book
    defs: list[Definition]
