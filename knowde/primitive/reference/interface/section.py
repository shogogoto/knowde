"""節."""
from __future__ import annotations

import click

from knowde.core.api.api_param import APIPath, APIQuery
from knowde.core.api.endpoint import (
    Endpoint,
    router2delete,
    router2get,
    router2put,
    router2tpost,
)
from knowde.core.cli.click_decorators import each_args
from knowde.core.cli.click_decorators.view.options import view_options
from knowde.core.cli.field.model2click import model2decorator
from knowde.core.cli.field.types import PrefUidParam
from knowde.primitive.reference.domain import Section
from knowde.primitive.reference.dto import HeadlineParam
from knowde.primitive.reference.repo.section import (
    add_section,
    change_section,
    complete_section,
    remove_section,
)

from .chapter import complete_chapter_client

sec_router = Endpoint.Section.create_router()
add_client = APIPath(name="chap_uid", prefix="").to_client(
    sec_router,
    router2tpost,
    add_section,
    t_body=HeadlineParam,
    convert=Section.of,
)

p_uid = APIPath(name="sec_uid", prefix="")
change_client = p_uid.to_client(
    sec_router,
    router2put,
    change_section,
    t_body=HeadlineParam,
    convert=Section.of,
)

complete_section_client = APIPath(name="", prefix="/completion").to_client(
    sec_router,
    router2get,
    complete_section,
    query=APIQuery(name="pref_uid"),
    convert=Section.of,
)
remove_req = p_uid.to_request(
    sec_router,
    router2delete,
    remove_section,
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
    converter=lambda pref_uid: complete_section_client(pref_uid=pref_uid),
)
def rm(s: Section) -> None:
    """節の削除."""
    remove_req(sec_uid=s.valid_uid)
    click.echo(f"{s}を削除しました")
