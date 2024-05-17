from __future__ import annotations

import click

from knowde._feature._shared.api.client_factory import ClientFactory, RouterConfig
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.cli.click_decorators import each_args
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature._shared.cli.field.types import PrefUidParam
from knowde._feature.reference.domain import Section
from knowde._feature.reference.dto import HeadlineParam
from knowde._feature.reference.repo.section import (
    add_section,
    change_section,
    complete_section,
    remove_section,
)

from .chapter import complete_chapter_client

sec_router = Endpoint.Section.create_router()
factory = ClientFactory(router=sec_router, rettype=Section)

add_client = factory.to_post(
    RouterConfig().path("chap_uid").body(HeadlineParam),
    add_section,
)

change_client = factory.to_put(
    RouterConfig().path("sec_uid").body(HeadlineParam),
    change_section,
)

remove_client = factory.to_delete(
    RouterConfig().path("sec_uid"),
    remove_section,
)


complete_section_client = factory.to_get(
    RouterConfig().path("", "/completion").query("pref_uid"),
    complete_section,
)


@click.group("section")
def sec_cli() -> None:
    """節(章の項目)に関するコマンド群."""


@sec_cli.command("add")
@model2decorator(PrefUidParam)
@model2decorator(HeadlineParam)
def add(pref_uid: str, **kwargs) -> None:  # noqa: ANN003
    """節の追加."""
    chap = complete_chapter_client(pref_uid=pref_uid)
    sec = add_client(chap_uid=chap.valid_uid, **kwargs)
    click.echo("以下を作成しました")
    click.echo(sec)


@sec_cli.command("ch")
@model2decorator(PrefUidParam)
@model2decorator(HeadlineParam)
@view_options
def ch(pref_uid: str, **kwargs) -> list[Section]:  # noqa: ANN003
    """節の変更."""
    pre = complete_section_client(pref_uid=pref_uid)
    post = change_client(chap_uid=pre.valid_uid, **kwargs)
    click.echo("0から1へ変更しました")
    return [pre, post]


@sec_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_chapter_client(pref_uid=pref_uid),
)
def rm(s: Section) -> None:
    """節の削除."""
    remove_client(chap_uid=s.valid_uid)
    click.echo(f"{s}を削除しました")
