"""floder DB."""
from __future__ import annotations

from pathlib import PurePath
from typing import TYPE_CHECKING

import networkx as nx
from neomodel import (
    db,
)

from knowde.complex.resource.category.folder import FolderSpace
from knowde.complex.resource.category.folder.label import LFolder
from knowde.complex.resource.category.folder.mapper import MFolder
from knowde.primitive.__core__.neoutil import to_uuid
from knowde.primitive.user.repo import LUser

from .errors import (
    FolderAlreadyExistsError,
    FolderNotFoundError,
)

if TYPE_CHECKING:
    from knowde.primitive.__core__.neoutil import UUIDy


def create_folder(user_id: UUIDy, *names: str) -> LFolder:
    """一般化フォルダ作成."""
    match len(names):
        case 0:
            msg = "フォルダ名を1つ以上指定して"
            raise ValueError(msg)
        case 1:
            return create_root_folder(user_id, names[0])
        case _:
            return create_sub_folder(user_id, *names)


def create_root_folder(user_id: UUIDy, name: str) -> LFolder:
    """直下フォルダ作成."""
    u: LUser = LUser.nodes.get(uid=to_uuid(user_id).hex)
    _f = LFolder.nodes.get_or_none(name=name)
    if _f is not None:
        raise FolderAlreadyExistsError
    f: LFolder = LFolder(name=name).save()
    f.owner.connect(u)
    return f


def create_sub_folder(user_id: UUIDy, root: str, *names: str) -> LFolder:
    """サブフォルダ作成."""
    if len(names) == 0:
        raise ValueError
    create_name = names[-1]
    parent, subs = fetch_subfolders(user_id, root, *names[:-1])
    if create_name in [s.name for s in subs if s is not None]:
        p = "/".join([root, *names])
        msg = f"/{p}'は既に存在しています"
        raise FolderAlreadyExistsError(msg)
    sub = LFolder(name=create_name).save()
    sub.parent.connect(parent)
    return sub


def fetch_subfolders(
    user_id: UUIDy,
    root: str,
    *names: str,
) -> tuple[LFolder, tuple[LFolder]]:
    """ネットワークを辿ってフォルダとそのサブフォルダを取得."""
    n = len(names)
    uid = to_uuid(user_id)
    qs = [
        f"MATCH (:User {{uid: $uid}})<-[:OWNED]-(f0:Folder {{ name: '{root}' }})",
        *[
            f"<-[:PARENT]-(f{i+1}:Folder {{ name: '{name}' }})"
            for i, name in enumerate(names)
        ],
        f"OPTIONAL MATCH (f{n})<-[:PARENT]-(sub:Folder)",
        f"RETURN f{n}, sub",
    ]
    q = "\n".join(qs)
    res = db.cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )[0]  # 1要素の2重リスト[[...]]のはず
    if len(res) == 0:
        p = "/".join(names)
        msg = f"フォルダ'/{p}'が見つからない"
        raise FolderNotFoundError(msg, res)

    targets, subs = zip(*res)
    return targets[0], subs


def fetch_folderspace(user_id: UUIDy) -> FolderSpace:
    """配下のサブフォルダ."""
    q = """
        MATCH (user:User {uid: $uid})
        OPTIONAL MATCH (user)<-[:OWNED]-(root:Folder)
        RETURN root as f1, null as f2
        UNION
        OPTIONAL MATCH (root)<-[:PARENT]-(sub:Folder)
        RETURN root as f1, sub as f2
        UNION
        OPTIONAL MATCH (sub)<-[:PARENT]-+(f1:Folder)<-[:PARENT]-(f2:Folder)
        RETURN f1, f2
    """
    uid = to_uuid(user_id)
    res = db.cypher_query(q, params={"uid": uid.hex}, resolve_objects=True)
    g = nx.DiGraph()
    roots = {}
    for f1, f2 in res[0]:
        if f2 is None:
            if f1 is not None:
                root_lb = MFolder.from_lb(f1)
                roots[f1.name] = root_lb
                g.add_node(root_lb)
            continue
        m1 = MFolder.from_lb(f1)
        m2 = MFolder.from_lb(f2)
        g.add_edge(m1, m2)
    return FolderSpace(roots_=roots, g=g)


def move_folder(user_id: UUIDy, target: PurePath | str, to: PurePath | str) -> LFolder:
    """フォルダの移動(配下ごと)."""
    target = PurePath(target)  # PathはOSのファイルシステムを参照するらしく不適
    to = PurePath(to)
    if not (target.is_absolute() and to.is_absolute()):
        msg = "絶対パスで指定して"
        raise ValueError(msg, target, to)
    fs = fetch_folderspace(user_id)
    tgt = fs.get_as_label(*target.parts[1:])
    tgt.parent.disconnect(tgt.parent.get())
    to_names = to.parts[1:]
    if len(to_names) == 0:  # rootへ
        luser = LUser.nodes.get(uid=user_id)
        tgt.owner.connect(luser)
        return tgt
    parent_to_move = fs.get_as_label(*to_names[:-1])
    tgt.parent.connect(parent_to_move)
    tgt.name = to_names[-1]
    return tgt.save()
