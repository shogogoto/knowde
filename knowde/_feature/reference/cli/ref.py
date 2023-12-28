from __future__ import annotations

from typing import TYPE_CHECKING

import click

from knowde._feature._shared import each_args
from knowde._feature._shared.view.options import view_options

from .repo import req_add, req_change_name, req_complete, req_list, req_rm

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
@each_args(
    "uids",
    converter=lambda pref_uid: req_complete(pref_uid).valid_uid,
)
def _remove(uid: UUID) -> None:
    return req_rm(uid)


@ref_cli.command("ch")
@click.argument("pref_uid", nargs=1, type=click.STRING)
@click.argument("name", nargs=1, type=click.STRING)
@view_options
def _change(
    pref_uid: str,
    name: str,
) -> list[Reference]:
    pre = req_complete(pref_uid)
    post = req_change_name(pre.valid_uid, name)
    click.echo("Reference was changed")
    return [pre, post]
