"""CLI引数の逐次変換."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import (
    Concatenate,
    ParamSpec,
    TextIO,
    TypeVar,
)

import click
from pydantic import BaseModel

from knowde.cli.util.typeutil.func import rename_argument

P = ParamSpec("P")
T = TypeVar("T")
type Wrapped[T, **P] = Callable[Concatenate[T, P], None]
type Param[**P] = Concatenate[tuple[str], TextIO, P]
type Return = Callable[Param, None]
type Converter[T] = Callable[[str], T]


class EachArgsWrapper[T](BaseModel, frozen=True):
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
            params = list(params___)
            if not file.isatty():
                lines = file.read().splitlines()
                params.extend(lines)

            converted = [self.converter(p) for p in params]
            for c in converted:
                func(c, *args, **kwargs)

        return wrapper


def each_args(
    arg_name: str = "params",
    converter: Converter = lambda x: x,
) -> Callable[[Wrapped], Return]:
    """Decorate with uuid completion."""
    return EachArgsWrapper(converter=converter, arg_name=arg_name)
