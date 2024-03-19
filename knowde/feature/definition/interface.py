"""define api and cli."""
from uuid import UUID

import click
from fastapi import status

from knowde._feature._shared.api.client_factory import (
    create_add_client,
    create_complete_client,
)
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.generate_req import APIRequests, inject_signature
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.dto import DetailParam, DetailView
from knowde.feature.definition.repo.definition import (
    add_definition,
    complete_definition,
)
from knowde.feature.definition.service import detail_service

def_router = Endpoint.Definition.create_router()
add_client = create_add_client(
    def_router,
    add_definition,
    DefinitionParam,
    Definition,
)

complete_client = create_complete_client(
    def_router,
    complete_definition,
    Definition,
)


reqs = APIRequests(router=def_router)
req_detail = reqs.get(
    inject_signature(detail_service, [UUID], DetailView),
    "/detail/{def_uid}",
)


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
    res = req_detail(relative=f"/detail/{d.valid_uid}")
    if res.status_code == status.HTTP_404_NOT_FOUND:
        click.echo(f"uid={pref_def_uid}...の定義は見つかりませんでした")
    DetailView.model_validate(res.json()).echo()
