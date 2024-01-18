from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    NamedTuple,
    Protocol,
    TypeVar,
)

import click
from pydantic import BaseModel, Field
from pydantic_partial.partial import create_partial_model
from starlette.status import HTTP_200_OK

from knowde._feature._shared.cli.to_clickparam import model2decorator
from knowde._feature._shared.domain import DomainModel

from . import each_args, view_options

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature._shared.endpoint import Endpoint


T = TypeVar("T", bound=DomainModel)


class _CompleteParam(BaseModel, frozen=True):
    pref_uid: str = Field(
        min_length=1,
        description="uuidと前方一致で検索",
    )


class CliRequestError(Exception):
    pass


class CommandHook(Protocol):
    def __call__(
        self,
        command_name: str,
        t_in: type[BaseModel],
        command_help: str | None = None,
    ) -> Callable:
        ...


class DocHook(Protocol):
    def __call__(
        self,
        command_name: str,
        command_help: str | None = None,
    ) -> Callable:
        ...


class CommandHooks(NamedTuple, Generic[T]):
    complete: Callable[[str], T]
    create_add: CommandHook
    create_change: CommandHook
    create_rm: DocHook
    create_ls: DocHook


def create_group(  # noqa: C901
    name: str,
    ep: Endpoint,
    t_model: type[DomainModel],
    g_help: str | None = None,
) -> tuple[click.Group, CommandHooks]:
    """エンドポイントと返り値の型を束縛した関数も返す."""

    @click.group(name, help=g_help)
    def g() -> None:
        pass

    def complete(pref_uid: str) -> t_model:
        res = ep.get(relative="/completion", params={"pref_uid": pref_uid})
        if res.status_code != HTTP_200_OK:
            msg = res.json()["detail"]["message"]
            msg = f"[{res.status_code}]:{msg}"
            raise CliRequestError(msg)
        return t_model.model_validate(res.json())

    def create_ls(
        command_name: str,
        c_help: str | None = f"Show list of {t_model.__name__}",
    ) -> Callable:
        @g.command(command_name, help=c_help)
        @view_options
        def _ls() -> list[t_model]:
            res = ep.get()
            return [t_model.model_validate(e) for e in res.json()]

        return _ls

    def create_rm(
        command_name: str,
        c_help: str | None = f"Remove {t_model.__name__} by list of uid prefixes",
    ) -> Callable:
        @g.command(command_name, help=c_help)
        @each_args("uids", converter=lambda pref_uid: complete(pref_uid).valid_uid)
        def _rm(uid: UUID) -> None:
            ep.delete(relative=uid.hex)
            click.echo(f"{t_model.__name__}({uid}) was removed.")

        return _rm

    # createではなくaddの方が短くて良い
    def create_add(
        command_name: str,
        t_in: type[BaseModel],
        c_help: str | None = f"Create {t_model.__name__}",
    ) -> Callable:
        @g.command(command_name, help=c_help)
        @model2decorator(t_in)
        @view_options
        def _add(**kwargs) -> t_model:  # noqa: ANN003
            p = t_in.validate(kwargs)
            res = ep.post(json=p.model_dump())
            m = t_model.model_validate(res.json())
            click.echo(f"{t_model.__name__} was created newly.")
            return m

        return _add

    def create_change(
        command_name: str,
        t_in: type[BaseModel],
        c_help: str | None = f"Change {t_model.__name__} properties",
    ) -> Callable:
        @g.command(command_name, help=c_help)
        @model2decorator(_CompleteParam)
        @model2decorator(create_partial_model(t_in))
        @view_options
        def _change(
            pref_uid: str,
            **kwargs,  # noqa: ANN003
        ) -> list[t_model]:
            pre = complete(pref_uid)
            d = t_in.model_validate(kwargs).model_dump()
            res = ep.put(
                relative=pre.valid_uid.hex,
                json=d,
            )
            post = t_model.model_validate(res.json())
            click.echo(f"{t_model.__name__} was changed from 0 to 1.")
            return [pre, post]

        return _change

    return g, CommandHooks(
        complete,
        create_add,
        create_change,
        create_rm,
        create_ls,
    )
