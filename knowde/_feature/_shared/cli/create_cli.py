from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import click
from click import Group
from pydantic import BaseModel, Field
from starlette.status import HTTP_200_OK

from knowde._feature._shared.api.basic_param import (
    CompleteParam,
    ListParam,
    RemoveParam,
)
from knowde._feature._shared.cli import each_args
from knowde._feature._shared.cli.to_request import HttpMethod
from knowde._feature._shared.cli.view.options import view_options
from knowde._feature._shared.domain import DomainModel

from .request import CliRequest  # noqa: TCH001

if TYPE_CHECKING:
    from requests import Response

T = TypeVar("T", bound=DomainModel)


class CliRequestError(Exception):
    pass


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

        def _complete_check(res: Response) -> None:
            if res.status_code != HTTP_200_OK:
                msg = res.json()["detail"]["message"]
                msg = f"[{res.status_code}]:{msg}"
                raise CliRequestError(msg)

        complete = self.req.method(
            HttpMethod.GET,
            CompleteParam,
        )

        _cli.command("rm")(
            each_args("uids", converter=lambda pref_uid: complete(pref_uid).valid_uid)(
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
