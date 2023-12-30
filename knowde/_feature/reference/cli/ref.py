from __future__ import annotations

from typing import TYPE_CHECKING

import click

from knowde._feature._shared import view_options
from knowde._feature._shared.cli.create_cli import CliGroupCreator

from .repo import ref_req, req_add, req_change_name

if TYPE_CHECKING:
    from knowde._feature.reference.domain.domain import Reference


ref_cli = CliGroupCreator(req=ref_req)("reference")


@ref_cli.command("add")
@click.argument("name", nargs=1)
def _add(name: str) -> Reference:
    return req_add(name)


@ref_cli.command("ch")
@click.argument("pref_uid", nargs=1, type=click.STRING)
@click.argument("name", nargs=1, type=click.STRING)
@view_options
def _change(
    pref_uid: str,
    name: str,
) -> list[Reference]:
    pre = ref_req.complete(pref_uid)
    post = req_change_name(pre.valid_uid, name)
    click.echo("Reference was changed")
    return [pre, post]
