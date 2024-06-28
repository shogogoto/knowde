"""define api and cli."""
from __future__ import annotations

import click

from knowde._feature._shared import Endpoint, each_args
from knowde._feature._shared.api.check_response import (
    check_delete,
    check_get,
    check_post,
)
from knowde._feature._shared.api.client_factory import (
    RouterConfig,
)
from knowde._feature._shared.api.generate_req import StatusCodeGrant
from knowde._feature._shared.api.paramfunc import to_apifunc
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.domain.statistics import StatsDefinitions
from knowde.feature.definition.dto import DetailParam, DetailView
from knowde.feature.definition.repo.definition import (
    add_definition,
    complete_definition,
    list_definitions,
    remove_definition,
)
from knowde.feature.definition.service import detail_service

def_router = Endpoint.Definition.create_router()
grant = StatusCodeGrant(router=def_router)
add_client = (
    RouterConfig()
    .body(DefinitionParam)
    .to_client(
        grant.to_post,
        to_apifunc(add_definition, DefinitionParam, Definition),
        Definition.of,
        check_post,
    ),
)
complete_client = (
    RouterConfig()
    .path("", "/completion")
    .query("pref_uid")
    .to_client(grant.to_get, complete_definition, Definition.of, check_get)
)
detail_client = (
    RouterConfig()
    .path("def_uid")
    .to_client(grant.to_get, detail_service, DetailView.of, check_get)
)
list_client = RouterConfig().to_client(
    grant.to_get,
    list_definitions,
    StatsDefinitions.of,
    check_get,
)
remove_req = RouterConfig().path("def_uid")(grant.to_delete, remove_definition)


@click.group("def")
def def_cli() -> None:
    """定義操作."""


@def_cli.command("add")
@model2decorator(DefinitionParam)
def add(**kwargs) -> None:  # noqa: ANN003
    """定義の追加."""
    d: Definition = add_client(**kwargs)
    click.echo("以下を作成しました")
    click.echo(d.output)
    for term in d.deps:
        click.echo(f"{term.value}({term.valid_uid})をマークしました")


@def_cli.command("detail")
@model2decorator(DetailParam)
def detail(pref_def_uid: str) -> None:
    """定義の依存関係含めて表示."""
    d = complete_client(pref_uid=pref_def_uid)
    detail_client(def_uid=d.valid_uid).echo()


@def_cli.command("ls")
def _ls() -> None:
    """定義一覧."""
    for d in list_client().values:
        click.echo(d.output)


@def_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def _rm(d: Definition) -> None:
    """定義を削除."""
    res = remove_req(def_uid=d.valid_uid)
    check_delete(res)
    click.echo(f"{d.output}を削除しました")
