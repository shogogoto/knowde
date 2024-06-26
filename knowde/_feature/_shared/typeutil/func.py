from __future__ import annotations

from inspect import Parameter, Signature, signature
from typing import (
    Any,
    Callable,
    Concatenate,
    ParamSpec,
)

from makefun import create_function

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
