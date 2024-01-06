from __future__ import annotations

import click

from knowde._feature._shared import view_options
from knowde._feature._shared.cli import set_basic_commands
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.reference.domain.domain import Reference

from .repo import ref_req, req_add, req_change_name


@click.group("reference")
def ref_cli() -> None:
    pass


set_basic_commands(ref_cli, ep=Endpoint.Reference, t_model=Reference)


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
