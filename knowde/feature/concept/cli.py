"""concept cli."""
from __future__ import annotations

from typing import Optional
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
    name: str = typer.Argument(),
    explain: Optional[str] = typer.Argument(),
) -> None:
    """Create concept."""
    c = ConceptProp(name=name, explain=explain)
    req_add(c)


@concept_cli.command("rm")
def remove(
    uid: UUID = typer.Argument(),  # noqa: B008
) -> None:
    """Remove concept."""
    req_remove(uid)


@concept_cli.command("ch")
def change(
    uid: UUID,
    name: Optional[str] = typer.Option(..., "--name", "-n"),
    explain: Optional[str] = typer.Option(..., "--explain", "-e"),
) -> None:
    """Change concept properties."""
    prop = ConceptChangeProp(
        name=name,
        explain=explain,
    )
    req_change(uid, prop)
