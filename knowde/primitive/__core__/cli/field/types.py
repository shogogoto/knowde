"""CLI field types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class ClickParamAttrs(TypedDict):
    """clickデコレータの共通属性."""

    # type: ParamType | Any | None


class OptionAttrs(ClickParamAttrs):
    """click option属性."""

    help: str | None
    default: Any
    nargs: int
    # show_default: bool | None


class ArgumentAttrs(ClickParamAttrs):
    """click argument属性."""

    nargs: int


class PrefUidParam(BaseModel, frozen=True):
    """UUIDの前方一致文字列."""

    pref_uid: str = Field(description="uuidへ前方一致で検索")
