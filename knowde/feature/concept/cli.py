"""concept cli."""
from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID  # noqa: TCH003

import typer

from .domain import ConceptChangeProp, ConceptProp
from .repo.api import req_add, req_change, req_list, req_remove

concept_cli = typer.Typer()


@concept_cli.command("ls")
def _list() -> None:
    """List concepts."""
    ls = req_list()
    typer.echo(ls)


# createは打数が多いからやめた
@concept_cli.command("add")
def add(
    name: Annotated[str, typer.Argument()],
    explain: Annotated[Optional[str], typer.Argument()],
) -> None:
    """Create concept."""
    c = ConceptProp(name=name, explain=explain)
    req_add(c)


@concept_cli.command("rm")
def remove(
    uid: Annotated[UUID, typer.Argument()],
) -> None:
    """Remove concept."""
    req_remove(uid)


@concept_cli.command("ch")
def change(
    uid: UUID,
    name: Annotated[Optional[str], typer.Option("-n")] = None,
    explain: Annotated[Optional[str], typer.Option("-e")] = None,
) -> None:
    """Change concept properties."""
    prop = ConceptChangeProp(name=name, explain=explain)
    req_change(uid, prop)
