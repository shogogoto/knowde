"""concept cli."""
from __future__ import annotations

import click

from knowde._feature._shared import view_options
from knowde._feature._shared.cli import set_basic_commands
from knowde._feature._shared.cli.click_wrapper import to_click_wrappers
from knowde._feature._shared.cli.request import CliRequest
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import Concept, ConceptProp
from knowde._feature.concept.domain.domain import ConceptChangeParam

req_concept = CliRequest(
    endpoint=Endpoint.Concept,
    M=Concept,
)


@click.group("concept")
def concept_cli() -> None:
    pass


_, utils = set_basic_commands(
    concept_cli,
    ep=Endpoint.Concept,
    t_model=Concept,
)


# createは打数が多いからやめた
@concept_cli.command("add")
@to_click_wrappers(ConceptProp).wraps
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
@to_click_wrappers(ConceptChangeParam).wraps
@view_options
def change(
    pref_uid: str,
    name: str | None,
    explain: str | None,
) -> list[Concept]:
    """Change concept properties."""
    prop = ConceptChangeParam(
        pref_uid=pref_uid,
        name=name,
        explain=explain,
    )
    pre = utils.complete(pref_uid)
    post = req_concept.put(pre.valid_uid, prop)
    click.echo("Concept was changed 0 -> 1")
    return [pre, post]
