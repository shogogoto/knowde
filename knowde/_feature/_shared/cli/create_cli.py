from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import click
from click import Group
from pydantic import BaseModel

from knowde._feature._shared.cli import each_args
from knowde._feature._shared.cli.view.options import view_options
from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from uuid import UUID

from knowde._feature._shared.cli.request import CliRequest  # noqa: TCH001

T = TypeVar("T", bound=DomainModel)


class CliGroupCreator(BaseModel, Generic[T], frozen=True):
    req: CliRequest

    def __call__(
        self,
        group_name: str,
        doc: str | None = None,
    ) -> Group:
        @click.group(group_name)
        def _cli() -> None:
            f"""{doc}"""  # noqa: B021

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
