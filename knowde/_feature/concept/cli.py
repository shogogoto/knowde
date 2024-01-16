"""concept cli."""
from __future__ import annotations

from knowde._feature._shared.cli import create_group
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import Concept, ConceptProp
from knowde._feature.concept.domain.domain import ConceptChangeParam

concept_cli, hooks = create_group(
    "concept",
    ep=Endpoint.Concept,
    t_model=Concept,
)


# createではなくaddの方がは打数が少ない
hooks.create_add("add", ConceptProp, "Concept was created newly.")

hooks.create_change("ch", ConceptChangeParam, None)

# concept_cli.command("ch")(
#     hooks.create_change(ConceptChangeParam, "Concept was changed 0 -> 1"),
# )
