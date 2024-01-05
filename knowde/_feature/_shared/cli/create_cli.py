from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import click
from click import Group
from pydantic import BaseModel, Field

from knowde._feature._shared.api.param import ApiParam  # noqa: TCH001
from knowde._feature._shared.cli import each_args
from knowde._feature._shared.cli.view.options import view_options
from knowde._feature._shared.domain import DomainModel

from .request import CliRequest  # noqa: TCH001

if TYPE_CHECKING:
    from uuid import UUID

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
