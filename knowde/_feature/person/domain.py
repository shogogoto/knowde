from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from datetime import date


class Author(DomainModel, frozen=True):
    name: str
    birth: date | None = None
    death: date | None = None
