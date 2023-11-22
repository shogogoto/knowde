"""concept cli."""
from __future__ import annotations

from typing import TYPE_CHECKING

import click

from .domain import Concept, ConceptChangeProp, ConceptProp
from .repo.api import req_add, req_change, req_list, req_remove

if TYPE_CHECKING:
    from uuid import UUID


@click.group("concept")
def concept_cli() -> None:
    """Concept group."""


@concept_cli.command("ls")
def _list() -> list[Concept]:
    """List concepts."""
    click.echo([e.model_dump() for e in req_list()])


arg_uid = click.argument("uid", nargs=1, type=click.UUID)
op_ex = click.option(
    "--explain",
    "-ex",
    default=None,
    type=click.STRING,
    show_default=True,
    help="説明文",
)


# createは打数が多いからやめた
@concept_cli.command("add")
@click.argument("name", nargs=1)
@op_ex
def add(
    name: str,
    explain: str | None,
) -> None:
    """Create concept."""
    c = ConceptProp(name=name, explain=explain)
    req_add(c)


@concept_cli.command("rm")
@arg_uid
def remove(uid: UUID) -> None:
    """Remove concept."""
    req_remove(uid)


@concept_cli.command("ch")
@arg_uid
@click.option(
    "--name",
    "-n",
    default=None,
    type=click.STRING,
)
@op_ex
def change(
    uid: UUID,
    name: str | None,
    explain: str | None,
) -> Concept:
    """Change concept properties."""
    prop = ConceptChangeProp(
        name=name,
        explain=explain,
    )
    return req_change(uid, prop)
