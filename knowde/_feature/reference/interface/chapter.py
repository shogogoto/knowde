from __future__ import annotations

import click

from knowde._feature.reference.domain import Chapter
from knowde._feature.reference.dto import HeadlineParam
from knowde._feature.reference.repo.chapter import (
    add_book_chapter,
    change_chapter,
    complete_chapter,
    remove_chapter,
)
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

chap_router = Endpoint.Chapter.create_router()
add_client = APIPath(name="book_uid", prefix="").to_client(
    chap_router,
    router2tpost,
    add_book_chapter,
    t_body=HeadlineParam,
    convert=Chapter.of,
)
p_uid = APIPath(name="chap_uid", prefix="")
change_client = p_uid.to_client(
    chap_router,
    router2put,
    change_chapter,
    t_body=HeadlineParam,
    convert=Chapter.of,
)
remove_req = p_uid.to_request(chap_router, router2delete, remove_chapter)
# ここでは定義順序によるバグは発生しない
# getメソッド同士があると発生するのかも
complete_chapter_client = APIPath(name="", prefix="/completion").to_client(
    chap_router,
    router2get,
    complete_chapter,
    query=APIQuery(name="pref_uid"),
    convert=Chapter.of,
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
    pre = complete_chapter_client(pref_uid=pref_uid)
    post = change_client(chap_uid=pre.valid_uid, **kwargs)
    click.echo("0から1へ変更しました")
    return [pre, post]


@chap_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_chapter_client(pref_uid=pref_uid),
)
def rm(c: Chapter) -> None:
    """章の削除."""
    remove_req(chap_uid=c.valid_uid)
    click.echo(f"{c}を削除しました")
