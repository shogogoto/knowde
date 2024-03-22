"""define api and cli."""
from __future__ import annotations

import click
from compose import compose

from knowde._feature._shared import Endpoint, each_args
from knowde._feature._shared.api.client_factory import (
    RequestPartial,
)
from knowde._feature._shared.api.generate_req import StatusCodeGrant
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
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
add_req = RequestPartial().body(DefinitionParam)(grant.to_post, add_definition)
complete_req = (
    RequestPartial()
    .path("", "/completion")
    .query("pref_uid")(grant.to_get, complete_definition)
)
detail_req = RequestPartial().path("def_uid")(grant.to_get, detail_service)
list_req = RequestPartial()(grant.to_get, list_definitions)
remove_req = RequestPartial().path("def_uid")(grant.to_delete, remove_definition)

add_client = compose(Definition.of, add_req)
complete_client = compose(Definition.of, complete_req)
detail_client = compose(DetailView.of, detail_req)
list_client = compose(Definition.ofs, list_req)


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
    for d in list_client():
        click.echo(d.output)


@def_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def _rm(d: Definition) -> None:
    """定義を削除."""
    remove_req(def_uid=d.valid_uid)
    click.echo(f"{d.output}を削除しました")
