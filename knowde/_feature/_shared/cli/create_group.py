from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, NamedTuple, Optional, TypeVar

import click
from starlette.status import HTTP_200_OK

from knowde._feature._shared.api.basic_param import (
    AddParam,
    ChangeParam,
    CompleteParam,
    ListParam,
    RemoveParam,
)
from knowde._feature._shared.cli.click_wrapper import to_click_wrappers
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


class CommandHooks(NamedTuple, Generic[T]):
    complete: Callable[[str], T]
    create_add: Callable[[type[AddParam], str], Callable]
    create_change: Callable[[type[ChangeParam], str], Callable]


def create_group(
    name: str,
    ep: Endpoint,
    t_model: type[DomainModel],
    g_help: str | None = None,
) -> tuple[click.Group, CommandHooks]:
    """エンドポイントと返り値の型を束縛した関数も返す."""

    @click.group(name, help=g_help)
    def g() -> None:
        pass

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

    def create_add(
        t_param: type[AddParam],
        message: Optional[str] = None,
    ) -> Callable:
        @to_click_wrappers(t_param).wraps
        @view_options
        def _add(**kwargs) -> t_model:  # noqa: ANN003
            post = HttpMethod.POST.request_func(
                ep=ep,
                param=t_param,
                return_converter=lambda res: t_model.model_validate(res.json()),
            )
            m = post(**kwargs)
            click.echo(message)
            return m

        return _add

    def create_change(
        t_param: type[ChangeParam],
        message: Optional[str] = None,
    ) -> Callable:
        @to_click_wrappers(CompleteParam).wraps
        @to_click_wrappers(t_param).wraps
        @view_options
        def _change(
            pref_uid: str,
            **kwargs,  # noqa: ANN003
        ) -> list[t_model]:
            """Change concept properties."""
            pre = complete(pref_uid)
            put = HttpMethod.PUT.request_func(
                ep=ep,
                param=t_param,
                return_converter=lambda res: t_model.model_validate(res.json()),
            )
            post = put(uid=pre.valid_uid, **kwargs)
            click.echo(message)
            return [pre, post]

        return _change

    return g, CommandHooks(
        complete,
        create_add,
        create_change,
    )
