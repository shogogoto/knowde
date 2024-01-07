from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, NamedTuple, TypeVar

import click
from starlette.status import HTTP_200_OK

from knowde._feature._shared.api.basic_param import (
    CompleteParam,
    ListParam,
    RemoveParam,
)
from knowde._feature._shared.domain import DomainModel

from .each_args import each_args
from .to_request import HttpMethod
from .view.options import view_options

if TYPE_CHECKING:
    from requests import Response

    from knowde._feature._shared.endpoint import Endpoint

T = TypeVar("T", bound=DomainModel)


class CliRequestError(Exception):
    pass


class BasicUtils(NamedTuple, Generic[T]):
    complete: Callable[[str], T]


def set_basic_commands(
    g: click.Group,
    ep: Endpoint,
    t_model: type[DomainModel],
) -> tuple[click.Group, BasicUtils]:
    def _complete_check(res: Response) -> None:
        if res.status_code != HTTP_200_OK:
            msg = res.json()["detail"]["message"]
            msg = f"[{res.status_code}]:{msg}"
            raise CliRequestError(msg)

    complete = HttpMethod.GET.request_func(
        ep=ep,
        param=CompleteParam,
        return_converter=lambda res: t_model.model_validate(res.json()),
        response_check=_complete_check,
    )

    g.command("rm")(
        each_args("uids", converter=lambda pref_uid: complete(pref_uid).valid_uid)(
            HttpMethod.DELETE.request_func(
                ep=ep,
                param=RemoveParam,
                return_converter=lambda _res: None,
                post_func=lambda uid: click.echo(f"{uid} was removed"),
            ),
        ),
    )

    g.command("ls")(
        view_options(
            HttpMethod.GET.request_func(
                ep=ep,
                param=ListParam,
                return_converter=lambda res: [
                    t_model.model_validate(e) for e in res.json()
                ],
            ),
        ),
    )

    return g, BasicUtils(complete)
