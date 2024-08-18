"""event interface."""
from __future__ import annotations

from uuid import UUID

import click

from knowde._feature._shared.api.api_param import NullPath
from knowde._feature._shared.api.const import CmplPath, CmplQ, UUIDPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_bodyfunc
from knowde._feature._shared.cli.click_decorators import each_args
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature._shared.cli.field.types import PrefUidParam
from knowde.complex.event.domain.event import Event
from knowde.complex.event.dto import AddEventParam, ChangeTextParam
from knowde.complex.event.repo.event import (
    add_event,
    change_event,
    complete_event,
    list_event,
)
from knowde.complex.event.repo.label import EventUtil

ev_router = Endpoint.Event.create_router()
cf = ClientFactory(router=ev_router, rettype=Event)
complete_client = cf.get(CmplPath, complete_event, query=CmplQ)
add_client = cf.post(
    NullPath(),
    to_bodyfunc(add_event, AddEventParam),
    t_body=AddEventParam,
)
list_client = cf.gets(NullPath(), list_event)
change_client = cf.put(
    UUIDPath,
    to_bodyfunc(change_event, ChangeTextParam, ignores=[("uid", UUID)]),
    t_body=ChangeTextParam,
)
remove_client = cf.delete(UUIDPath, EventUtil.delete)


@click.group("ev")
def event_cli() -> None:
    """出来事."""


@event_cli.command("add")
@model2decorator(AddEventParam)
def _add(**kwargs) -> None:  # noqa: ANN003
    """追加."""
    p = add_client(**kwargs)
    click.echo("以下を追加しました")
    click.echo(p.output)


@event_cli.command("ls")
@view_options
def _ls() -> list[Event]:
    """一覧."""
    return list_client()


@event_cli.command("ch")
@model2decorator(PrefUidParam)
@model2decorator(ChangeTextParam)
@view_options
def _ch(pref_uid: str, text: str) -> list[Event]:
    """名前変更."""
    pre = complete_client(pref_uid=pref_uid)
    post = change_client(uid=pre.valid_uid, text=text)
    click.echo("0->1に変更しました")
    return [pre, post]


@event_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def _rm(p: Event) -> None:
    """削除."""
    remove_client(uid=p.valid_uid)
    click.echo(f"{p.output}を削除しました")
