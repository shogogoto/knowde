"""floder DB."""

from __future__ import annotations

from datetime import date
from pathlib import PurePath
from typing import TYPE_CHECKING

from knowde.feature.entry import ResourceMeta
from knowde.feature.entry.errors import EntryAlreadyExistsError
from knowde.feature.entry.label import LFolder, LResource
from knowde.feature.entry.namespace import (
    fetch_namespace,
    fill_parents,
    save_resource,
)
from knowde.shared.types import UUIDy
from knowde.shared.user.label import LUser

if TYPE_CHECKING:
    pass


async def create_folder(user_id: UUIDy, *names: str) -> LFolder:
    """一般化フォルダ作成."""
    ns = await fetch_namespace(user_id)
    return await fill_parents(ns, *names)


async def create_resource(
    user_id: UUIDy,
    *names: str,
    authors: list[str] | None = None,
    published: date | None = None,
    urls: list[str] | None = None,
) -> LResource:
    """リソース作成."""
    if len(names) == 0:
        msg = "フォルダ名を1つ以上指定して"
        raise ValueError(msg)

    m = ResourceMeta(
        title=names[-1],
        authors=authors or [],
        published=published,
        urls=urls or [],
        path=tuple(names[:-1]) if len(names) > 1 else None,
    )
    ns = await fetch_namespace(user_id)
    r = await save_resource(m, ns)
    if r is None:
        msg = f"{names[-1]} は既に存在します"
        raise EntryAlreadyExistsError(msg)
    return r


async def move_folder(
    user_id: UUIDy,
    target: PurePath | str,
    to: PurePath | str,
) -> LFolder:
    """フォルダの移動(配下ごと)."""
    target = PurePath(target)  # PathはOSのファイルシステムを参照するらしく不適
    to = PurePath(to)
    if not (target.is_absolute() and to.is_absolute()):
        msg = "絶対パスで指定して"
        raise ValueError(msg, target, to)
    fs = await fetch_namespace(user_id)
    tgt = LFolder(**fs.get(*target.parts[1:]).model_dump())
    p = await tgt.parent.get()
    await tgt.parent.disconnect(p)
    to_names = to.parts[1:]
    if len(to_names) == 0:  # rootへ
        luser = await LUser.nodes.get(uid=user_id)
        await tgt.owner.connect(luser)
        return tgt
    parent_to_move = LFolder(**fs.get(*to_names[:-1]).model_dump())
    await tgt.parent.connect(parent_to_move)
    tgt.name = to_names[-1]
    return await tgt.save()


# def delete_entry(user_id: UUIDy, *names: str) -> None:
#     """配下ごと削除."""
#     # entry特定
#     # resource => 削除 & sysnode削除
#     # folder => 削除 & resource 再帰的削除
#     q = """
#         MATCH (user:User {uid: $uid})
#         OPTIONAL MATCH (user)<-[:OWNED]-(root:Folder)
#         RETURN root as f1, null as f2
#         OPTIONAL MATCH (root)<-[:PARENT]-(sub:Folder)
#         RETURN root as f1, sub as f2
#         UNION
#         OPTIONAL MATCH (sub)<-[:PARENT]-+(f1:Folder)<-[:PARENT]-(f2:Folder)
#         RETURN f1, f2
#     """
#     uid = to_uuid(user_id)
#     res = db.cypher_query(q, params={"uid": uid.hex}, resolve_objects=True)
