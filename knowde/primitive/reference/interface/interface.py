"""いろいろ."""
from __future__ import annotations

import click

from knowde.core.api.api_param import APIPath, APIQuery, NullPath
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
from knowde.core.typeutil import inject_signature
from knowde.primitive.reference.domain import Book, Reference, ReferenceTree
from knowde.primitive.reference.dto import BookParam, PartialBookParam
from knowde.primitive.reference.interface.chapter import chap_cli
from knowde.primitive.reference.interface.section import sec_cli
from knowde.primitive.reference.repo.book import (
    add_book,
    change_book,
    complete_book,
)
from knowde.primitive.reference.repo.label import BookUtil
from knowde.primitive.reference.repo.reference import find_reftree, remove_ref

book_router = Endpoint.Book.create_router()
add_book_client = NullPath().to_client(
    book_router,
    router2tpost,
    add_book,
    t_body=BookParam,
    convert=Book.of,
)
complete_book_client = APIPath(name="", prefix="/completion").to_client(
    book_router,
    router2get,
    complete_book,
    query=APIQuery(name="pref_uid"),
    convert=Book.of,
)
p_uid = APIPath(name="ref_uid", prefix="")
remove_client = p_uid.to_request(
    book_router,
    router2delete,
    remove_ref,
)
list_client = NullPath().to_client(
    book_router,
    router2get,
    inject_signature(BookUtil.find, [], list[Book]),
    convert=Book.ofs,
)
change_client = p_uid.to_client(
    book_router,
    router2put,
    change_book,
    t_body=PartialBookParam,
    convert=Book.of,
)
detail_client = p_uid.to_client(
    book_router,
    router2get,
    find_reftree,
    convert=ReferenceTree[Book].of,
)


@click.group("ref")
def ref_cli() -> None:
    """参考情報源."""


ref_cli.add_command(chap_cli)
ref_cli.add_command(sec_cli)


@ref_cli.command("detail")
@model2decorator(PrefUidParam)
def detail(pref_uid: str) -> None:
    """詳細."""
    r = complete_book_client(pref_uid=pref_uid)
    d = detail_client(ref_uid=r.valid_uid)
    click.echo(d.output)


@ref_cli.command("add_book")
@model2decorator(BookParam)
def add_book_(**kwargs) -> None:  # noqa: ANN003
    """本の追加."""
    book: Book = add_book_client(**kwargs)
    click.echo("以下を作成しました")
    click.echo(book.output)


# @ref_cli.command("add_web")
# # @model2decorator(WebParam)
# def add_web(**kwargs) -> None:
#     click.echo(kwargs)


@ref_cli.command("ls")
@view_options
def ls() -> list[Book]:
    """一覧."""
    return list_client()


@ref_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_book_client(pref_uid=pref_uid),
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
    """本の変更."""
    pre = complete_book_client(pref_uid=pref_uid)
    post = change_client(ref_uid=pre.valid_uid, **kwargs)
    click.echo("0から1へ変更しました")
    return [pre, post]
