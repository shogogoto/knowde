"""Data transfer object."""
from __future__ import annotations

from pydantic import BaseModel, Field

from knowde.core.domain.container import Composite  # noqa: TCH001
from knowde.core.domain.domain import APIReturn
from knowde.primitive.location.domain import Location  # noqa: TCH001


class LocationAddParam(BaseModel, frozen=True):
    """API定義用."""

    name: str = Field(description="場所名")


class LocationDetailView(APIReturn, frozen=True):
    """GenericのままAPIReturnするとjson decodeに失敗するので中間層."""

    detail: Composite[Location] = Field(description="xxx")
