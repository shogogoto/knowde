"""concept cli."""
from __future__ import annotations

from knowde._feature._shared.cli import create_group
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import Concept, ConceptProp

concept_cli, hooks = create_group(
    "concept",
    ep=Endpoint.Concept,
    t_model=Concept,
)


hooks.create_add("add", ConceptProp)
hooks.create_change("ch", ConceptProp)
hooks.create_rm("rm")
hooks.create_ls("ls")
