from __future__ import annotations

import re
from inspect import Parameter, Signature, signature
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    ForwardRef,
    ParamSpec,
)

from makefun import create_function
from pydantic_core import PydanticUndefined

if TYPE_CHECKING:
    from pydantic import BaseModel
    from pydantic.fields import FieldInfo

P = ParamSpec("P")


class VariadicArgumentsUndefinedError(Exception):
    """*args, **kwargs引数が定義されていないっ関数は対象外."""


def rename_argument(old: str, new: str) -> Callable[[Callable], Callable]:
    def wrapper(f: Callable[Concatenate[..., P], Any]) -> Callable:
        sig = signature(f)
        plist = list(sig.parameters.values())

        variadics = [
            p
            for p in plist
            if p.kind in {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}
        ]
        if len(variadics) == 0:
            raise VariadicArgumentsUndefinedError

        p_old = next(p for p in plist if p.name == old)
        p_new = p_old.replace(name=new)
        i = plist.index(p_old)
        plist.pop(i)
        plist.insert(i, p_new)
        return create_function(
            sig.replace(parameters=plist),
            f,
        )

    return wrapper


def inject_signature(
    f: Callable,
    t_in: list[type],
    t_out: type | None = None,
) -> Callable:
    """API定義時に型情報が喪失する場合があるので、それを補う."""
    params = signature(f).parameters.values()
    replaced = []
    if len(t_in) != 0:
        for p, t in zip(params, t_in, strict=True):
            p_new = p.replace(annotation=t)
            replaced.append(p_new)
    return create_function(
        Signature(replaced, return_annotation=t_out),
        f,
    )


class MappingField2ArgumentError(Exception):
    """fieldとargのマッピングエラー."""


def eq_fieldparam_type(p: Parameter, f: FieldInfo) -> bool:
    """引数とfieldの型を比較."""
    pt = p.annotation
    ft = f.annotation

    if isinstance(ft, ForwardRef):  # ft is primitive
        return pt == ft.__forward_arg__
    x = re.findall(r"<class '(.*)'>", str(ft))
    return pt == x[0].split(".")[-1]


def check_map_fields2params(t: type[BaseModel], f: Callable) -> None:
    """引数とfieldが一致するか[name, type, default]."""
    fields = t.model_fields
    params = signature(f).parameters

    keys_p = set(params.keys())
    keys_f = set(fields.keys())

    extra_p = keys_p - keys_f
    if len(extra_p) > 0:
        msg = "func args are extra {extra_p}"
        raise MappingField2ArgumentError(msg)
    extra_f = keys_f - keys_p
    if len(extra_f) > 0:
        msg = "fields arg extra {extra_f}"
        raise MappingField2ArgumentError(msg)

    for k, p in params.items():
        if k not in fields:
            msg = f"{k} is not in arguments"
            raise MappingField2ArgumentError(msg)
        field = fields[k]
        if not eq_fieldparam_type(p, field):
            t = p.annotation
            msg = f"{k} field type [{field.annotation}] != argument type [{t}]"
            raise MappingField2ArgumentError(msg)
        is_fd_none = field.default == PydanticUndefined
        is_pd_none = p.default == Parameter.empty
        if is_fd_none and is_pd_none:
            continue
        if field.default != p.default:
            d = p.default
            msg = f"{k} field default [{field.default}] != argument default [{d}]"
            raise MappingField2ArgumentError(msg)
