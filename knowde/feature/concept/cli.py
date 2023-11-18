"""concept cli."""

from typing import Annotated
from uuid import UUID

import typer

from knowde.feature._shared.endpoint import Endpoint
from knowde.feature.concept.domain import ConceptProp

concept_cli = typer.Typer()


@concept_cli.command("ls")
def _list() -> None:
    """List concepts."""
    typer.echo(Endpoint.Concept.get().json())


@concept_cli.command()
def add(c: ConceptProp) -> None:
    """Create concept."""
    Endpoint.Concept.post(json=c.model_dump())


@concept_cli.command("rm")
def remove(uid: Annotated[UUID, typer.Argument()]) -> None:
    """Remove concept."""
    Endpoint.Concept.Delete(uid.hex)
