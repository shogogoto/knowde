"""concept cli."""
from __future__ import annotations

import click

from knowde._feature._shared import view_options
from knowde._feature._shared.cli.create_cli import CliGroupCreator
from knowde._feature._shared.cli.request import CliRequest
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import ChangeProp, Concept, ConceptProp

req_concept = CliRequest(
    endpoint=Endpoint.Concept,
    M=Concept,
)
concept_cli = CliGroupCreator(req=req_concept)("concept")


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
    m = req_concept.post(c)
    click.echo("Concept was created newly")
    return m


@concept_cli.command("ch")
@click.argument("pref_uid", nargs=1, type=click.STRING)
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
) -> list[Concept]:
    """Change concept properties."""
    prop = ChangeProp(
        name=name,
        explain=explain,
    )
    pre = req_concept.complete(pref_uid)
    post = req_concept.put(pre.valid_uid, prop)
    click.echo("Concept was changed 0 -> 1")
    return [pre, post]
