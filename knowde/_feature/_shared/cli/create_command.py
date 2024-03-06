from __future__ import annotations

from typing import (
    TYPE_CHECKING,
)

import click
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.api.generate_req import inject_signature
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.funcparam.func2click import func2clickparams
from knowde._feature._shared.cli.to_click import click_decorate

from . import each_args

if TYPE_CHECKING:
    from uuid import UUID

    from pydantic import BaseModel

    from knowde._feature._shared.api.client_factory import APIClientFactory


def set_basic_commands(
    g: click.Group,
    factory: APIClientFactory,
) -> None:
    """独自のclickparamが存在しないコマンド."""
    clients = factory.create_basics()
    out_name = factory.t_out.__name__

    @g.command("ls", help="一覧表示")
    @view_options
    def ls():  # noqa: ANN202
        return clients.ls()

    @g.command("rm", help="削除")
    @each_args(
        "uids",
        converter=lambda pref_uid: clients.complete(pref_uid).valid_uid,
    )
    def rm(uid: UUID) -> None:
        clients.rm(uid)
        click.echo(f"remove {out_name}({uid})")


def set_add_change_command(
    g: click.Group,
    factory: APIClientFactory,
    t_in: type[BaseModel],
) -> None:
    add = factory.create_add(t_in)
    addparams = func2clickparams(
        inject_signature(add, [t_in]),
    )
    out_name = factory.t_out.__name__

    @g.command("add", help="追加")
    @click_decorate(addparams)
    @view_options
    def _add(**kwargs):  # noqa: ANN202 ANN003
        m = add(**kwargs)
        click.echo(f"{out_name} was created newly.")
        return m

    ch = factory.create_change(t_in)
    OPT = create_partial_model(t_in)  # noqa: N806

    chparams = func2clickparams(
        inject_signature(ch, [str, OPT]),
    )

    @g.command("ch", help="変更")
    @click_decorate(chparams)
    @view_options
    def _change(**kwargs):  # noqa: ANN202 ANN003
        pre, post = ch(**kwargs)
        click.echo(f"{out_name} was changed from 0 to 1.")
        return [pre, post]
