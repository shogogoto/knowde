from __future__ import annotations

from typing import Generic, TypeVar

import click
from click import Group
from pydantic import BaseModel, Field

from knowde._feature._shared.api.basic_param import ListParam, RemoveParam
from knowde._feature._shared.cli.to_request import HttpMethod
from knowde._feature._shared.cli.view.options import view_options
from knowde._feature._shared.domain import DomainModel

from .request import CliRequest  # noqa: TCH001

T = TypeVar("T", bound=DomainModel)


class CliGroupCreator(BaseModel, Generic[T]):
    req: CliRequest = Field(frozen=True)
    group_help: str = Field(default="", frozen=True)

    def __call__(
        self,
        group_name: str,
    ) -> Group:
        @click.group(group_name, help=self.group_help)
        def _cli() -> None:
            pass

        _cli.command("rm")(
            self.req.each_complete("uids")(
                self.req.noreturn_method(
                    HttpMethod.DELETE,
                    RemoveParam,
                    post_func=lambda uid: click.echo(f"{uid} was removed"),
                ),
            ),
        )

        _cli.command("ls")(
            view_options(
                self.req.ls_method(
                    HttpMethod.GET,
                    ListParam,
                ),
            ),
        )

        return _cli
