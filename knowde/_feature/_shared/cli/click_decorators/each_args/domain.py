from __future__ import annotations

import functools
from inspect import Parameter, signature
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    TextIO,
    TypeAlias,
    TypeVar,
)

import click
from makefun import create_function
from pydantic import BaseModel

P = ParamSpec("P")
T = TypeVar("T")
Wrapped: TypeAlias = Callable[Concatenate[T, P], None]
Param: TypeAlias = Concatenate[tuple[str], TextIO, P]
Return: TypeAlias = Callable[Param, None]
Converter: TypeAlias = Callable[[str], T]


class EachArgsWrapper(BaseModel, Generic[T], frozen=True):
    """wrap command."""

    converter: Converter[T]
    arg_name: str

    def __call__(self, func: Wrapped) -> Return:
        """標準入力からもuuidを取得できるオプション."""

        @click.argument(self.arg_name, nargs=-1, type=click.STRING)
        @click.option(
            "--file",
            "-f",
            type=click.File("r"),
            default="-",
            help="対象のUUIDをファイル入力(default:標準入力)",
        )
        @functools.wraps(func)  # docstringを引き継ぐ
        @rename_argument("params___", self.arg_name)
        def wrapper(
            params___: tuple[str],  # 名前衝突を避けるための___
            file: TextIO,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> None:
            _params = list(params___)
            if not file.isatty():
                lines = file.read().splitlines()
                _params.extend(lines)

            converted = [self.converter(p) for p in _params]
            for c in converted:
                func(c, *args, **kwargs)

        return wrapper


def each_args(
    arg_name: str = "params",
    converter: Converter = lambda x: x,
) -> Callable[[Wrapped], Return]:
    """Decorate with uuid completion."""
    return EachArgsWrapper(converter=converter, arg_name=arg_name)


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


class VariadicArgumentsUndefinedError(Exception):
    """*args, **kwargs引数が定義されていないっ関数は対象外."""
