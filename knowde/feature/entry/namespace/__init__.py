"""リソースの詳細(knowde)を含まないリソースのメタ情報repo."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from itertools import pairwise
from pathlib import Path, PurePath
from uuid import UUID

import neo4j
import networkx as nx
from neomodel.async_.core import AsyncDatabase
from pydantic import RootModel

from knowde.feature.entry import NameSpace, ResourceMeta
from knowde.feature.entry.errors import (
    DuplicatedTitleError,
    EntryAlreadyExistsError,
    SaveResourceError,
)
from knowde.feature.entry.label import LFolder, LResource
from knowde.feature.entry.mapper import MFolder, MResource
from knowde.feature.knowde import ResourceOwner
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.user.label import LUser
from knowde.shared.user.schema import UserReadPublic


class ResourceMetas(RootModel[list[ResourceMeta]]):
    """リクエスト用."""

    def check_duplicated_title(self) -> None:
        """titleの重複を許さない."""
        titles = [m.title for m in self.root]
        if len(titles) != len(set(titles)):
            msg = "titleが重複しています"
            raise DuplicatedTitleError(msg, titles)


async def fetch_namespace(user_id: UUIDy) -> NameSpace:
    """ユーザー配下のサブフォルダ."""
    q = """
        MATCH (user:User {uid: $uid})
            , p = (user)<-[:OWNED|PARENT]-*(:Entry)
        RETURN p
    """
    uid = to_uuid(user_id)
    res = await AsyncDatabase().cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )

    g = nx.DiGraph()
    ns = NameSpace(roots_={}, g=g, user_id=uid)

    for p in res[0]:
        path: neo4j.graph.Path = p[0]
        for e1, e2 in pairwise(path.nodes):
            if isinstance(e1, LUser):
                ns.add_root(e2.frozen)
            else:
                ns.add_edge(e1.frozen, e2.frozen)
    return ns


async def fill_parents(ns: NameSpace, *names: str) -> LFolder | None:
    """フォルダをDB上で繋げてtailを返す."""
    if len(names) == 0:
        return None
    path = ns.get_path(*names)
    tail = next((p for p in reversed(path) if p is not None), None)
    match tail:
        case None:  # 新規作成 = tail なし = 既存親なし
            u: LUser = await LUser.nodes.get(uid=ns.user_id.hex)
            folders = await LFolder.create(*[{"name": name} for name in names])
            head: LFolder = folders[0]
            await head.owner.connect(u)
            ns.add_root(head.frozen)
            for f1, f2 in pairwise(folders):
                await f2.parent.connect(f1)
                ns.add_edge(f1.frozen, f2.frozen)
            return folders[-1]
        case MFolder():  # フォルダが途中まで既存
            i = path.index(tail) + 1  # not none の最初の位置
            folders = await LFolder.create(*[{"name": name} for name in names[i:]])
            folders = [LFolder(**tail.model_dump()), *folders]
            for f1, f2 in pairwise(folders):
                await f2.parent.connect(f1)
                ns.g.add_edge(f1.frozen, f2.frozen)
            return folders[-1]
        case _:
            raise ValueError


async def save_resource(m: ResourceMeta, ns: NameSpace) -> LResource | None:
    """新規作成 or 更新して返す."""
    path = ns.get_path(*m.names)
    tail = next((p for p in reversed(path) if p is not None), None)
    match tail:
        case None | MFolder():  # 新規作成 or フォルダが途中まで既存
            lb = await LResource(**m.model_dump()).save()
            parent = await fill_parents(ns, *m.names[:-1])
            if parent is None:  # user直下
                u = await LUser.nodes.get(uid=ns.user_id.hex)
                await lb.owner.connect(u)
                ns.add_root(lb.frozen)
            else:
                await lb.parent.connect(parent)
                ns.add_edge(parent.frozen, lb.frozen)
            return lb
        case MResource():  # 更新
            if m.txt_hash == tail.txt_hash:  # 変更なし
                return None
            lb = LResource(**tail.model_dump())
            for k, v in m.model_dump().items():
                setattr(lb, k, v)
            return await lb.save()
        case _:
            raise ValueError


async def save_or_move_resource(m: ResourceMeta, ns: NameSpace) -> LResource | None:
    """移動を反映してsave."""
    # NSに重複したタイトルがあると困る
    old = ns.get_resource_or_none(m.title)
    if old is None:  # 新規
        return await save_resource(m, ns)
    ns.remove_resource(m.title)
    old = await LResource(**old.model_dump()).save()  # reflesh
    owner = await old.owner.get_or_none()
    parent = await old.parent.get_or_none()
    if owner is None and parent is None:
        msg = "所有者も親もなかったなんてあり得ないからね"
        raise SaveResourceError(msg)
    if parent is None:  # owner直下
        await old.owner.disconnect(owner)
    else:
        await old.parent.disconnect(parent)
    new_parent = await fill_parents(ns, *m.names[:-1])
    if new_parent is None:  # user直下
        u = await LUser.nodes.get(uid=ns.user_id.hex)
        await old.owner.connect(u)
        ns.add_root(old.frozen)
    else:
        await old.parent.connect(new_parent)
        ns.add_edge(new_parent.frozen, old.frozen)
    return old


async def sync_namespace(metas: ResourceMetas, ns: NameSpace) -> list[Path]:
    """変更や移動されたファイルパスをDBに反映して変更があったものを返す."""
    metas.check_duplicated_title()
    ls = []
    for m in metas.root:
        e = ns.get_or_none(*m.names)
        if e is None:
            lb = await save_or_move_resource(m, ns)
        else:
            lb = await save_resource(m, ns)
        if lb is not None:
            ls.append(Path().joinpath(*m.path))
    return ls


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


async def resource_owners_by_resource_uids(
    resource_uids: Iterable[UUID],
) -> dict[UUID, ResourceOwner]:
    """resource_uidの各々のリソースの所有者を返す."""
    q = """
        UNWIND $uids as uid
        MATCH p = (user:User)<-[:OWNED|PARENT]-*(r:Resource {uid: uid})
        RETURN DISTINCT p
        """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"uids": list({uid.hex for uid in resource_uids})},
    )
    d = {}
    for row in rows:
        path: neo4j.graph.Path = row[0]
        resource_path = [p.get("name") for p in path.nodes[1:]]
        r = MResource.freeze_dict(path.end_node)
        d[r.uid] = ResourceOwner(
            user=UserReadPublic.model_validate(path.start_node),
            resource=r.model_copy(
                update={"path": tuple(e for e in resource_path if e is not None)},
            ),
        )
    return d


async def fetch_owner_by_resource_uid(resource_uid: UUIDy) -> ResourceOwner:
    """Wrap tool for resource info."""
    uid = to_uuid(resource_uid)
    owners = await resource_owners_by_resource_uids([uid])
    return owners[uid]
