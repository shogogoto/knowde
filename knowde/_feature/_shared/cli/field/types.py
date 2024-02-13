from __future__ import annotations

from typing import TypedDict


class ClickParamAttrs(TypedDict):
    pass
    # type: ParamType | Any | None


class OptionAttrs(ClickParamAttrs):
    help: str | None
    # show_default: bool | None


class ArgumentAttrs(ClickParamAttrs):
    pass
