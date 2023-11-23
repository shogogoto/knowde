"""concept cli."""
from __future__ import annotations

from typing import TYPE_CHECKING

import click

from knowde.feature._shared import each_args
from knowde.feature._shared.view.options import view_options
from knowde.feature.concept.domain import ConceptChangeProp, ConceptProp
from knowde.feature.concept.repo.repo import complete_concept

from .repo import req_add, req_change, req_list, req_remove

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.feature.concept.domain import Concept


@click.group("concept")
def concept_cli() -> None:
    """Concept group."""


@concept_cli.command("ls")
@view_options
def _list() -> list[Concept]:
    """List concepts."""
    return req_list()


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
@view_options
def add(
    name: str,
    explain: str | None,
) -> Concept:
    """Create concept."""
    c = ConceptProp(name=name, explain=explain)
    click.echo("Concept was created newly")
    return req_add(c)


@concept_cli.command("rm")
@each_args(
    "uids",
    converter=lambda pref_uid: complete_concept(pref_uid).valid_uid,
)
def remove(uid: UUID) -> None:
    """Remove concept."""
    req_remove(uid)
    click.echo(f"Concept({uid}) was deleted")


@concept_cli.command("ch")
@click.argument("uid", nargs=1, type=click.STRING)
@arg_uid
@click.option(
    "--name",
    "-n",
    default=None,
    type=click.STRING,
)
@op_ex
@view_options
def change(
    pref_uid: str,
    name: str | None,
    explain: str | None,
) -> Concept:
    """Change concept properties."""
    prop = ConceptChangeProp(
        name=name,
        explain=explain,
    )
    uid = complete_concept(pref_uid).valid_uid
    req_change(uid, prop)
    click.echo("Concept was changed")
