from __future__ import annotations

from typing import Any, TypedDict

from pydantic import BaseModel, Field


class ClickParamAttrs(TypedDict):
    pass
    # type: ParamType | Any | None


class OptionAttrs(ClickParamAttrs):
    help: str | None
    default: Any
    # show_default: bool | None


class ArgumentAttrs(ClickParamAttrs):
    pass


class PrefUidParam(BaseModel, frozen=True):
    pref_uid: str = Field(description="uuidへ前方一致で検索")
