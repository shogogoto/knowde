from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from uuid import UUID

import click
from click import Command, ParamType
from pydantic import RootModel

from knowde._feature._shared.api.param import ApiParam  # noqa: TCH001

if TYPE_CHECKING:
    from pydantic.main import TupleGenerator


def type2type(t: type | None) -> ParamType:
    if t == str:
        return click.STRING
    if t == float:
        return click.FLOAT
    if t == UUID:
        return click.UUID
    if t == int:
        return click.INT
    if t == bool:
        return click.BOOL
    msg = f"{t} is not compatible type"
    raise ValueError(msg)


Wrapper = Callable[[Callable], Callable]


class ClickWrappers(RootModel[list[Wrapper]], frozen=True):
    def __iter__(self) -> TupleGenerator:
        """Behavior like list."""
        return iter(self.root)

    def __next__(self) -> Wrapper:
        """Behavior like list."""
        return next(self.root)

    def __len__(self) -> int:
        """Count of elements."""
        return len(self.root)

    def __getitem__(self, i: int) -> Wrapper:
        """Indexing."""
        return self.root[i]

    def wraps(self, command_func: Callable) -> Command:
        f = command_func
        for w in self.root:
            f = w(f)
        return click.command(f)

    def get_by_name(self, name: str) -> Wrapper | None:
        for w in self.root:
            if w.name == name:
                return w
        return None


def to_click_wrappers(
    param: ApiParam,
) -> ClickWrappers:
    """click.{argument,option}のリストを返す."""
    cliparams = []
    for k, v in param.model_fields.items():
        if v.is_required():
            p = click.argument(
                k,
                nargs=1,
                type=type2type(v.annotation),
            )
        else:
            t = type(getattr(param, k))  # for excliding optional
            p = click.option(
                f"--{k}",
                f"-{k[0]}",
                type=type2type(t),
                help=v.description,
            )
        cliparams.append(p)
    return ClickWrappers(root=cliparams)
