from __future__ import annotations

from inspect import isclass
from types import UnionType
from typing import TYPE_CHECKING, Callable, get_args
from uuid import UUID

import click
from click import ParamType
from pydantic import BaseModel, RootModel

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

    def wraps(self, command_func: Callable) -> Callable:
        f = command_func
        for w in self.root:
            f = w(f)
        return f


def to_click_wrappers(
    t_param: type[BaseModel],
    exclude: bool = True,  # noqa: FBT001 FBT002
) -> ClickWrappers:
    """click.{argument,option}のリストを返す."""
    params = []

    for k, v in t_param.model_fields.items():
        if exclude and v.exclude:
            continue
        t = v.annotation
        if isclass(t) and BaseModel in t.__mro__:
            ws = to_click_wrappers(t)
            params = list(reversed(params + ws.root))
        if type(t) == type and v.is_required():
            p = click.argument(
                k,
                nargs=1,
                type=type2type(t),
            )
            params.append(p)
        if type(t) == UnionType:
            t_exclude = get_args(t)[0]  # for excliding optional
            p = click.option(
                f"--{k}",
                f"-{k[0]}",
                type=type2type(t_exclude),
                help=v.description,
            )
            params.append(p)
    return ClickWrappers(root=params)
