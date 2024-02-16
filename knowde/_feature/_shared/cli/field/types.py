from __future__ import annotations

from typing import Any, TypedDict


class ClickParamAttrs(TypedDict):
    pass
    # type: ParamType | Any | None


class OptionAttrs(ClickParamAttrs):
    help: str | None
    default: Any
    # show_default: bool | None


class ArgumentAttrs(ClickParamAttrs):
    pass
