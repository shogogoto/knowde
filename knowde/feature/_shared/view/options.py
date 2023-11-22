"""view cli wrapper."""
from __future__ import annotations

import functools
from typing import Callable, ParamSpec, Sequence, TypeVar

import click
from pydantic import BaseModel

from knowde.feature._shared.view.domain import filter_props_json

from .domain import view

P = ParamSpec("P")
T = TypeVar("T", bound=BaseModel)
Wrapped = Callable[P, T | Sequence[T]]
Ret = Sequence[T]


def view_options(f: Wrapped) -> Callable:
    """CLI結果表示用共通オプション."""

    @click.option(
        "--property",
        "-P",
        "props",
        help="表示属性[複数指定可]",
        multiple=True,
        default=(),
        show_default=True,
    )
    @click.option(
        "--style",
        "-S",
        help="表示形式",
        default="table",
        type=click.Choice(["table", "json", "rows"]),
        show_default=True,
    )
    @functools.wraps(f)
    def _wrapper(
        props: tuple[str],
        style: str,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Ret:
        models = f(*args, **kwargs)
        if not isinstance(models, list):
            models = [models]
        if models is None:
            models = []
        filter_props_json(models, props)
        view(models, props, style)
        return models

    return _wrapper
