from __future__ import annotations

import click

from knowde._feature._shared.api.client_factory import ClientFactory, RouterConfig
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.cli.click_decorators import each_args
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature._shared.cli.field.types import PrefUidParam
from knowde._feature.reference.domain import Chapter
from knowde._feature.reference.dto import HeadlineParam
from knowde._feature.reference.repo.chapter import (
    add_book_chapter,
    change_chapter,
    complete_chapter,
    remove_chapter,
)

chap_router = Endpoint.Chapter.create_router()
factory = ClientFactory(router=chap_router, rettype=Chapter)

add_client = factory.to_post(
    RouterConfig().path("book_uid").body(HeadlineParam),
    add_book_chapter,
)

change_client = factory.to_put(
    RouterConfig().path("chap_uid").body(HeadlineParam),
    change_chapter,
)

remove_client = factory.to_delete(
    RouterConfig().path("chap_uid"),
    remove_chapter,
)


complete_client = factory.to_get(
    RouterConfig().path("", "/completion").query("pref_uid"),
    complete_chapter,
)


@click.group("chapter")
def chap_cli() -> None:
    """章に関するコマンド群."""


@chap_cli.command("add")
@model2decorator(PrefUidParam)
@model2decorator(HeadlineParam)
def add(pref_uid: str, **kwargs) -> None:  # noqa: ANN003
    """章の追加."""
    from .interface import complete_book_client  # for avoiding cyclic import

    book = complete_book_client(pref_uid=pref_uid)
    chap = add_client(book_uid=book.valid_uid, **kwargs)
    click.echo("以下を作成しました")
    click.echo(chap)


@chap_cli.command("ch")
@model2decorator(PrefUidParam)
@model2decorator(HeadlineParam)
@view_options
def ch(pref_uid: str, **kwargs) -> list[Chapter]:  # noqa: ANN003
    """章タイトルの変更."""
    pre = complete_client(pref_uid=pref_uid)
    post = change_client(chap_uid=pre.valid_uid, **kwargs)
    click.echo("0から1へ変更しました")
    return [pre, post]


@chap_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def rm(c: Chapter) -> None:
    """章の削除."""
    remove_client(chap_uid=c.valid_uid)
    click.echo(f"{c}を削除しました")
