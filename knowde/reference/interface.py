"""定義と参考文献を紐付けたい.

ref def add [ref_uid|chap_uid|sec_uid] title sentence
ref conn [ref_uid|chap_uid|sec_uid] def_uid
ref disconn [ref_uid|chap_uid|sec_uid] def_uid


Todo:
----
referred def
    refとdefの紐付け
    refでの定義数をカウント
    chapでの定義数のカウント
    secでの定義数のカウント

defの統計値
    defのrootsの取得
        rootsごとの距離も取得
    defのleavesの取得
        leavesごとの居見も取得
    defのsourcesのカウント


"""
from __future__ import annotations

import click

from knowde.complex.definition.domain.domain import DefinitionParam
from knowde.core.api.api_param import APIPath, NullPath
from knowde.core.api.endpoint import Endpoint, router2get, router2tpost
from knowde.core.cli.field.model2click import model2decorator
from knowde.core.cli.field.types import PrefUidParam
from knowde.primitive.reference.interface.reference import complete_ref_client
from knowde.reference.domain import RefDefinition, RefDefinitions
from knowde.reference.dto import RefDefParam
from knowde.reference.repo.definition import add_refdef, list_refdefs

refdef_router = Endpoint.RefDef.create_router()
add_client = NullPath().to_client(
    refdef_router,
    router2tpost,
    add_refdef,
    t_body=RefDefParam,
    convert=RefDefinition.of,
)
list_client = APIPath(name="ref_uid", prefix="").to_client(
    refdef_router,
    router2get,
    list_refdefs,
    convert=RefDefinitions.of,
)

# conn_client = (
#     RouterConfig()
#     .body(ConnectRefDefParam)
#     .to_client(
#         grant.to_post,
#         connect_def2ref,
#         none_return,
#         check_post,
#     )
# )


@click.group("def")
def refdef_cli() -> None:
    """引用付き定義関連."""


@refdef_cli.command("add")
@model2decorator(PrefUidParam)
@model2decorator(DefinitionParam)
def _add(pref_uid: str, **kwargs) -> None:  # noqa: ANN003
    """追加."""
    r = complete_ref_client(pref_uid=pref_uid)
    rd = add_client(ref_uid=r.valid_uid, **kwargs)
    click.echo("以下を作成しました")
    click.echo(rd.output)


@refdef_cli.command("ls")
@model2decorator(PrefUidParam)
def _ls(pref_uid: str) -> None:
    """追加."""
    r = complete_ref_client(pref_uid=pref_uid)
    rds = list_client(ref_uid=r.valid_uid)
    click.echo(rds.output)


########## 要らないと思うのでコメントアウト

# @refdef_cli.command("conn")
# @model2decorator(PrefUidParam)
# @model2decorator(DefUidParam)
# def _conn(pref_uid: str, def_uids: list[UUID]) -> None:
#     """定義を引用と紐付ける."""
#     r = complete_ref_client(pref_uid=pref_uid)


# @refdef_cli.command("disconn")
# @model2decorator(PrefUidParam)
# def _disconn(pref_uid: str) -> None:
#     """参考."""


# @refdef_cli.command("replace")
# @model2decorator(DoublePrefUidParam)
# def _replace(pref_uid1: str, pref_uid2: str) -> None:
#     """参考."""
#     r1 = complete_ref_client(pref_uid=pref_uid1)
#     r2 = complete_ref_client(pref_uid=pref_uid2)
