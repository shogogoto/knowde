from __future__ import annotations

from pydantic import BaseModel, Field

from knowde._feature.location.domain import Location  # noqa: TCH001
from knowde.core.domain.container import Composite  # noqa: TCH001
from knowde.core.domain.domain import APIReturn


class LocationAddParam(BaseModel, frozen=True):
    name: str = Field(description="場所名")


class LocationDetailView(APIReturn, frozen=True):
    """GenericのままAPIReturnするとjson decodeに失敗するので中間層."""

    detail: Composite[Location] = Field(description="xxx")
