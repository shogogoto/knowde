from __future__ import annotations

import click

from knowde._feature._shared.api.client_factory import ClientFactory, RouterConfig
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.generate_req import StatusCodeGrant, inject_signature
from knowde._feature._shared.cli.click_decorators import each_args
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature._shared.cli.field.types import PrefUidParam
from knowde._feature.reference.domain import Book, Reference, ReferenceTree
from knowde._feature.reference.dto import BookParam, PartialBookParam
from knowde._feature.reference.repo.book import (
    add_book,
    change_book,
    find_reftree,
    remove_book,
)
from knowde._feature.reference.repo.label import BookUtil

ref_router = Endpoint.Book.create_router()
grant = StatusCodeGrant(router=ref_router)
book_factory = ClientFactory(router=ref_router, rettype=Book)

add_book_client = book_factory.to_post(
    RouterConfig().body(BookParam),
    add_book,
)
complete_client = book_factory.to_get(
    RouterConfig().path("", "/completion").query("pref_uid"),
    lambda pref_uid: BookUtil.complete(pref_uid).to_model(),
)
remove_client = book_factory.to_delete(
    RouterConfig().path("ref_uid"),
    remove_book,
)

list_client = book_factory.to_gets(
    RouterConfig(),
    inject_signature(BookUtil.find, [], list[Book]),
)

change_client = book_factory.to_put(
    RouterConfig().path("ref_uid").body(PartialBookParam),
    change_book,
)

detail_factory = ClientFactory(router=ref_router, rettype=ReferenceTree)
detail_client = detail_factory.to_get(
    RouterConfig().path("ref_uid"),
    find_reftree,
)


@click.group("ref")
def ref_cli() -> None:
    """参考情報源."""


@ref_cli.command("add")
@model2decorator(BookParam)
def add(**kwargs) -> None:  # noqa: ANN003
    """本の追加."""
    book: Book = add_book_client(**kwargs)
    click.echo("以下を作成しました")
    click.echo(book)


@ref_cli.command("ls")
@view_options
def ls() -> list[Book]:
    return list_client()


@ref_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def rm(r: Reference) -> None:
    """参照情報源とその配下を削除."""
    remove_client(ref_uid=r.valid_uid)
    click.echo(f"{r}を削除しました")


@ref_cli.command("ch")
@model2decorator(PrefUidParam)
@model2decorator(PartialBookParam)
@view_options
def ch(pref_uid: str, **kwargs) -> list[Book]:  # noqa: ANN003
    pre = complete_client(pref_uid=pref_uid)
    post = change_client(ref_uid=pre.valid_uid, **kwargs)
    click.echo("0から1へ変更しました")
    return [pre, post]
