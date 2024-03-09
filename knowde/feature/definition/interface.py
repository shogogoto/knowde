"""define api and cli."""
import click

from knowde._feature._shared.api.client_factory import create_add_client
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde.feature.definition.domain.domain import Definition, DefinitionParam
from knowde.feature.definition.repo.definition import add_definition

def_router = Endpoint.Definition.create_router()
add_client = create_add_client(
    def_router,
    add_definition,
    DefinitionParam,
    Definition,
)


@click.group("def")
def def_cli() -> None:
    """定義操作."""


@def_cli.command("add")
@model2decorator(DefinitionParam)
def add(**kwargs) -> Definition:  # noqa: ANN003
    """定義の追加."""
    return add_client(**kwargs)
