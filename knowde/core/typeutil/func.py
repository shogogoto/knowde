"""関数関連の型."""
from __future__ import annotations

import re
from inspect import Parameter, Signature, signature
from types import GenericAlias
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    ForwardRef,
    Mapping,
    Optional,
    ParamSpec,
)

from makefun import create_function
from pydantic_core import PydanticUndefined

from knowde.core.typeutil.check import is_option

if TYPE_CHECKING:
    from pydantic import BaseModel
    from pydantic.fields import FieldInfo

P = ParamSpec("P")


class VariadicArgumentsUndefinedError(Exception):
    """*args, **kwargs引数が定義されていないっ関数は対象外."""


def rename_argument(old: str, new: str) -> Callable[[Callable], Callable]:
    """*argsと**kwargsがないとなんか失敗する."""

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
    name: Optional[str] = None,
) -> Callable:
    """API定義時に型情報が喪失する場合があるので、それを補う."""
    if name is None:
        name = f.__name__
    params = signature(f).parameters.values()
    replaced = []
    if len(t_in) != 0:
        for p, t in zip(params, t_in, strict=True):
            p_new = p.replace(annotation=t)
            replaced.append(p_new)
    return create_function(
        Signature(replaced, return_annotation=t_out),
        f,
        func_name=name,
    )


class MappingField2ArgumentError(Exception):
    """fieldとargのマッピングエラー."""


def _lastname(typestr: str) -> str:
    """FQCN -> N. e.g. uuid.UUID -> UUID."""
    return typestr.split(".")[-1]


def eq_fieldparam_type(p: Parameter, f: FieldInfo) -> bool:
    """引数とfieldの型を比較."""
    pt = p.annotation
    ft = f.annotation
    if isinstance(pt, type):
        return pt == ft
    if isinstance(ft, ForwardRef):  # ft is primitive
        return pt == ft.__forward_arg__
    if isinstance(ft, GenericAlias):  # e.g. list[UUID]
        px = re.findall(r"(.*)\[(.*)\]", str(pt))
        fx = re.findall(r"(.*)\[(.*)\]", str(ft))
        eq_alias = px[0][0] == fx[0][0]
        eq_ln = _lastname(px[0][1]) == _lastname(fx[0][1])
        return eq_alias and eq_ln
    if is_option(ft):
        return _lastname(str(ft)) == _lastname(str(pt))
    x = re.findall(r"<class '(.*)'>", str(ft))
    return pt == _lastname(x[0])


def check_eq_fieldparam_keys(
    t: type[BaseModel],
    params: Mapping[str, Parameter],
) -> None:
    """引数とfieldのkeysが一致するか."""
    keys_f = set(t.model_fields.keys())
    keys_p = set(params.keys())
    extra_p = keys_p - keys_f
    if len(extra_p) > 0:
        msg = f"func args are extra {extra_p}"
        raise MappingField2ArgumentError(msg)
    extra_f = keys_f - keys_p
    if len(extra_f) > 0:
        msg = f"fields arg extra {extra_f}"
        raise MappingField2ArgumentError(msg)


def check_map_fields2params(
    t: type[BaseModel],
    params: Mapping[str, Parameter],
) -> None:
    """引数とfieldが一致するか[name, type, default]."""
    check_eq_fieldparam_keys(t, params)
    fields = t.model_fields
    for k, p in params.items():
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
