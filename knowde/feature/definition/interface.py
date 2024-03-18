"""define api and cli."""
from uuid import UUID

import click

from knowde._feature._shared.api.client_factory import (
    create_add_client,
    create_basic_clients,
)
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.generate_req import APIRequests, inject_signature
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature.term.repo.label import TermUtil
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.dto import DetailView, TermIdParam
from knowde.feature.definition.repo.definition import (
    add_definition,
)
from knowde.feature.definition.service import detail_service

def_router = Endpoint.Definition.create_router()
add_client = create_add_client(
    def_router,
    add_definition,
    DefinitionParam,
    Definition,
)

clients = create_basic_clients(util=TermUtil, router=def_router)
reqs = APIRequests(router=def_router)
req_detail = reqs.get(
    inject_signature(detail_service, [UUID], DetailView),
    "/{term_uid}",
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
    for term in d.deps:
        click.echo(f"{term.value}({term.valid_uid})をマークしました")


@def_cli.command("detail")
@model2decorator(TermIdParam)
def detail(pref_term_uid: str) -> None:
    """定義の依存関係含めて表示."""
    term = clients.complete(pref_uid=pref_term_uid)
    res = req_detail(relative=str(term.valid_uid))
    DetailView.model_validate(res.json()).echo()
