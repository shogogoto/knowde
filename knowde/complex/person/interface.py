"""person interface."""
from __future__ import annotations

from uuid import UUID

import click

from knowde._feature._shared.api.api_param import NullPath
from knowde._feature._shared.api.const import CmplPath, CmplQ, UUIDPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_bodyfunc
from knowde._feature._shared.cli.click_decorators import each_args
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature._shared.cli.field.types import PrefUidParam
from knowde.complex.person.domain.person import Person
from knowde.complex.person.dto import PersonAddParam, PersonRenameParam
from knowde.complex.person.repo.label import PersonUtil
from knowde.complex.person.repo.repo import (
    add_person,
    complete_person,
    list_person,
    rename_person,
)

person_router = Endpoint.Person.create_router()
cf = ClientFactory(router=person_router, rettype=Person)
complete_client = cf.get(CmplPath, complete_person, query=CmplQ)
add_client = cf.post(
    NullPath(),
    to_bodyfunc(add_person, PersonAddParam),
    t_body=PersonAddParam,
)
list_client = cf.gets(NullPath(), list_person)
rename_client = cf.put(
    UUIDPath,
    to_bodyfunc(rename_person, PersonRenameParam, ignores=[("uid", UUID)]),
    t_body=PersonRenameParam,
)
remove_client = cf.delete(UUIDPath, PersonUtil.delete)


@click.group("person")
def person_cli() -> None:
    """人物."""


@person_cli.command("add")
@model2decorator(PersonAddParam)
def _add(**kwargs) -> None:  # noqa: ANN003
    """追加."""
    p = add_client(**kwargs)
    click.echo("以下を追加しました")
    click.echo(p.output)


@person_cli.command("ls")
@view_options
def _ls() -> list[Person]:
    """一覧."""
    return list_client()


@person_cli.command("rename")
@model2decorator(PrefUidParam)
@model2decorator(PersonRenameParam)
@view_options
def _rename(pref_uid: str, name: str) -> list[Person]:
    """名前変更."""
    pre = complete_client(pref_uid=pref_uid)
    post = rename_client(uid=pre.valid_uid, name=name)
    click.echo("0->1に変更しました")
    return [pre, post]


@person_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def _rm(p: Person) -> None:
    """削除."""
    remove_client(uid=p.valid_uid)
    click.echo(f"{p.output}を削除しました")
