from __future__ import annotations

import click

from knowde._feature._shared.api.check_response import check_get, check_post, check_put
from knowde._feature._shared.api.client_factory import RouterConfig
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

ref_router = Endpoint.Reference.create_router()
grant = StatusCodeGrant(router=ref_router)

add_book_client = (
    RouterConfig()
    .body(BookParam)
    .to_client(
        grant.to_post,
        add_book,
        Book.of,
        check_post,
    )
)

complete_client = (
    RouterConfig()
    .path("", "/completion")
    .query("pref_uid")
    .to_client(
        grant.to_get,
        lambda pref_uid: BookUtil.complete(pref_uid).to_model(),
        Book.of,
        check_get,
    )
)

detail_client = (
    RouterConfig()
    .path("ref_uid")
    .to_client(
        grant.to_get,
        find_reftree,
        ReferenceTree[Book].of,
        check_get,
    )
)
remove_req = RouterConfig().path("ref_uid")(grant.to_delete, remove_book)

list_client = RouterConfig().to_client(
    grant.to_get,
    inject_signature(BookUtil.find, [], list[Book]),
    Book.ofs,
    check_get,
)

change_client = (
    RouterConfig()
    .path("ref_uid")
    .body(PartialBookParam)
    .to_client(
        grant.to_put,
        change_book,
        Book.of,
        check_put,
    )
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
    remove_req(ref_uid=r.valid_uid)
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
