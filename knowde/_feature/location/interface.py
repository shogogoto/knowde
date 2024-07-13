from __future__ import annotations

from uuid import UUID

import click

from knowde._feature._shared.api.api_param import NullPath
from knowde._feature._shared.api.const import CmplPath, CmplQ, UUIDPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_bodyfunc, to_queryfunc
from knowde._feature._shared.cli.click_decorators import each_args
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature._shared.cli.field.types import PrefUidParam
from knowde._feature.location.domain import Location
from knowde._feature.location.dto import LocationAddParam
from knowde._feature.location.repo.label import LocUtil
from knowde._feature.location.repo.repo import (
    add_location_root,
    add_sub_location,
    list_location_root,
    remove_location,
    rename_location,
)

loc_router = Endpoint.Location.create_router()
cf = ClientFactory(router=loc_router, rettype=Location)

complete_client = cf.get(
    CmplPath,
    to_queryfunc(
        LocUtil.complete,
        [str],
        Location,
        lambda x: x.to_model(),
    ),
    query=CmplQ,
)

rename_client = cf.put(UUIDPath, rename_location)
add_client = cf.post(
    NullPath(),
    to_bodyfunc(add_location_root, LocationAddParam),
    t_body=LocationAddParam,
)
list_client = cf.gets(NullPath(), list_location_root)
add_sub_client = cf.post(
    UUIDPath,
    to_bodyfunc(add_sub_location, LocationAddParam, ignores=[("uid", UUID)]),
    t_body=LocationAddParam,
)
rm_client = cf.delete(UUIDPath, remove_location)
# detail_client = UUIDPath.to_client(
#     loc_router,
#     router2get,
#     detail_location_service,
#     convert=LocationDetailView.of,
# )


@click.group("locate")
def loc_cli() -> None:
    """場所."""


@loc_cli.command("add")
@model2decorator(LocationAddParam)
def _add(name: str) -> None:
    """追加."""
    loc = add_client(name=name)
    click.echo("以下を追加しました.")
    click.echo(loc.output)


@loc_cli.command("add_div")
@model2decorator(PrefUidParam)
@model2decorator(LocationAddParam)
def _add_div(pref_uid: str, name: str) -> None:
    """区分追加."""
    parent = complete_client(pref_uid=pref_uid)
    loc = add_sub_client(uid=parent.valid_uid, name=name)
    click.echo("以下を追加しました.")
    click.echo(f"{loc.output} IN {parent.output} ")


@loc_cli.command("ls")
@view_options
def _ls() -> list[Location]:
    """一覧."""
    return list_client()


@loc_cli.command("rename")
@model2decorator(PrefUidParam)
@model2decorator(LocationAddParam)
@view_options
def _rename(pref_uid: str, name: str) -> list[Location]:
    """名前変更."""
    pre = complete_client(pref_uid=pref_uid)
    post = rename_client(uid=pre.valid_uid, name=name)
    click.echo("0->1へ変更しました")
    return [pre, post]


@loc_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_client(pref_uid=pref_uid),
)
def _rm(loc: Location) -> None:
    """削除."""
    rm_client(uid=loc.valid_uid)
    click.echo(f"{loc.output}を削除しました")


# @loc_cli.command("detail")
# @model2decorator(PrefUidParam)
# def _detail(pref_uid: str) -> None:
#     """詳細."""
#     parent = complete_client(pref_uid=pref_uid)
#     print(parent)
#     d = detail_client(uid=parent.valid_uid)
#     print(d)
#     # return find
