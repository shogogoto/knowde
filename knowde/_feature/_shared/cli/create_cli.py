from __future__ import annotations

from typing import Callable, Generic, TypeVar
from uuid import UUID

import click
from click import Group, ParamType
from pydantic import BaseModel, Field

from knowde._feature._shared.api.param import ApiParam  # noqa: TCH001
from knowde._feature._shared.cli import each_args
from knowde._feature._shared.cli.view.options import view_options
from knowde._feature._shared.domain import DomainModel

from .request import CliRequest  # noqa: TCH001

T = TypeVar("T", bound=DomainModel)


class CliGroupCreator(BaseModel, Generic[T]):
    req: CliRequest = Field(frozen=True)
    group_help: str = Field(default="", frozen=True)
    commands: list[ApiParam] = Field(default_factory=list)

    def __call__(
        self,
        group_name: str,
    ) -> Group:
        @click.group(group_name, help=self.group_help)
        def _cli() -> None:
            pass

        @_cli.command("rm")
        @each_args(
            "uids",
            converter=lambda pref_uid: self.req.complete(pref_uid).valid_uid,
        )
        def _rm(uid: UUID) -> None:
            """Remove by uid."""
            self.req.rm(uid)
            click.echo(f"{uid} was removed")

        @_cli.command("ls")
        @view_options
        def _ls() -> list[T]:
            return self.req.ls()

        return _cli

    def add_command(self, param: ApiParam) -> None:
        pass


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


def to_click_wrapper(
    param: ApiParam,
) -> list[Wrapper]:
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
            )
        cliparams.append(p)
    return cliparams
