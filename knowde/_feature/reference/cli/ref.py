from __future__ import annotations

from typing import TYPE_CHECKING

import click

from knowde._feature._shared.view.options import view_options

from .repo import req_add, req_list, req_rm

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.reference.domain.domain import Reference


@click.group("reference")
def ref_cli() -> None:
    pass


@ref_cli.command("ls")
@view_options
def _list() -> list[Reference]:
    return req_list()


@ref_cli.command("add")
@click.argument("name", nargs=1)
def _add(name: str) -> Reference:
    return req_add(name)


@ref_cli.command("rm")
@click.argument("uid", nargs=1, type=click.UUID)
def _remove(uid: UUID) -> None:
    return req_rm(uid)
