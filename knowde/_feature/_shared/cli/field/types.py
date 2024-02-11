from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from click import ParamType

# ClickParam: TypeAlias = Callable[[FC], FC]


# def field2clicktype(info: FieldInfo) -> ParamType:
#     t = extract_type(info.annotation)
#     return to_clicktype(t)


class ClickParamAttrs(TypedDict):
    type: ParamType | Any | None


class OptionAttrs(ClickParamAttrs):
    help: str | None
    # show_default: bool | None


class ArgumentAttrs(ClickParamAttrs):
    pass
