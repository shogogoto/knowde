"""concept cli."""
from __future__ import annotations

import click

from knowde._feature._shared.cli import set_basic_commands
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import Concept, ConceptProp
from knowde._feature.concept.domain.domain import ConceptChangeParam


@click.group("concept")
def concept_cli() -> None:
    pass


_, utils = set_basic_commands(
    concept_cli,
    ep=Endpoint.Concept,
    t_model=Concept,
)


# createではなくaddの方がは打数が少ない
concept_cli.command("add")(
    utils.create_add(ConceptProp, "Concept was created newly."),
)


concept_cli.command("ch")(
    utils.create_change(ConceptChangeParam, "Concept was changed 0 -> 1"),
)
