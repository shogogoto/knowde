# proposition
from __future__ import annotations

from uuid import UUID

import click

from knowde._feature.proposition.domain import Proposition
from knowde._feature.proposition.dto import PropositionParam
from knowde._feature.proposition.repo.repo import (
    add_proposition,
    change_proposition,
    complete_proposition,
    delete_proposition,
    list_propositions,
)
from knowde.core.api.api_param import APIPath, APIQuery, NullPath
from knowde.core.api.endpoint import Endpoint
from knowde.core.api.facade import ClientFactory
from knowde.core.api.paramfunc import to_bodyfunc
from knowde.core.cli.click_decorators import each_args
from knowde.core.cli.click_decorators.view.options import view_options
from knowde.core.cli.field.model2click import model2decorator
from knowde.core.cli.field.types import PrefUidParam

p_router = Endpoint.Proposition.create_router()
pf = ClientFactory(router=p_router, rettype=Proposition)

add_client = pf.post(
    NullPath(),
    to_bodyfunc(add_proposition, PropositionParam),
    t_body=PropositionParam,
)
complete_proposition_client = pf.get(
    APIPath(name="", prefix="/completion"),
    complete_proposition,
    query=APIQuery(name="pref_uid"),
)
pid = APIPath(name="uid", prefix="")
_change = to_bodyfunc(
    change_proposition,
    PropositionParam,
    ignores=[("uid", UUID)],
)
change_client = pf.put(pid, _change, t_body=PropositionParam)
delete_client = pf.delete(pid, delete_proposition)
list_client = pf.gets(NullPath(), list_propositions)


@click.group("prop")
def prop_cli() -> None:
    """命題."""


@prop_cli.command("ls")
@view_options
def _ls() -> list[Proposition]:
    """一覧."""
    return list_client()


@prop_cli.command("add")
@model2decorator(PropositionParam)
@view_options
def _add(text: str) -> Proposition:
    """追加."""
    p = add_client(text=text)
    click.echo("以下を作成しました")
    return p


@prop_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_proposition_client(pref_uid=pref_uid),
)
def _rm(p: Proposition) -> None:
    """削除."""
    delete_client(uid=p.valid_uid)
    click.echo("以下を削除しました")
    click.echo(p)


@prop_cli.command("ch")
@model2decorator(PrefUidParam)
@model2decorator(PropositionParam)
@view_options
def _ch(pref_uid: str, text: str) -> list[Proposition]:
    """変更."""
    pre = complete_proposition_client(pref_uid=pref_uid)
    post = change_client(uid=pre.valid_uid, text=text)
    click.echo("0->1に変更しました")
    return [pre, post]
