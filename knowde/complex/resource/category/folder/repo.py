"""floder DB."""
from __future__ import annotations

from pathlib import PurePath
from typing import TYPE_CHECKING

import networkx as nx
from neomodel import (
    INCOMING,
    Traversal,
    db,
)

from knowde.complex.resource.label import LEntry, LFolder, LResource
from knowde.primitive.__core__.neoutil import to_uuid
from knowde.primitive.user.repo import LUser

from . import NameSpace
from .errors import (
    EntryAlreadyExistsError,
    EntryNotFoundError,
)

if TYPE_CHECKING:
    from datetime import date

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


def create_resource(
    user_id: UUIDy,
    *names: str,
    authors: list[str] | None = None,
    published: date | None = None,
    urls: list[str] | None = None,
) -> LResource:
    """リソース作成."""
    d = {"authors": authors, "published": published, "urls": urls}
    match len(names):
        case 0:
            msg = "フォルダ名を1つ以上指定して"
            raise ValueError(msg)
        case 1:
            return create_root_resource(user_id, names[0], **d)
        case _:
            return create_sub_resource(user_id, *names, **d)


def check_already_root(lb: LUser, name: str) -> None:
    """ユーザー直下でnameが既にあるか."""
    trav = Traversal(lb, "OWNED", {"node_class": LEntry, "direction": INCOMING})
    roots = trav.all()
    if name in [r.name for r in roots]:
        raise EntryAlreadyExistsError


def create_root_folder(user_id: UUIDy, name: str) -> LFolder:
    """直下フォルダ作成."""
    u: LUser = LUser.nodes.get(uid=to_uuid(user_id).hex)
    check_already_root(u, name)
    f: LFolder = LFolder(name=name).save()
    f.owner.connect(u)
    return f


def create_root_resource(
    user_id: UUIDy,
    name: str,
    authors: list[str] | None = None,
    published: date | None = None,
    urls: list[str] | None = None,
) -> LResource:
    """ユーザー直下のリソース."""
    u: LUser = LUser.nodes.get(uid=to_uuid(user_id).hex)
    check_already_root(u, name)
    d = {
        "title": name,
        "authors": authors,
        "published": published,
        "urls": urls,
    }
    r = LResource(**d)
    r.save()
    r.owner.connect(u)
    return r


def check_and_get_parent(user_id: UUIDy, root: str, *names: str) -> LFolder:
    """配下に同名のentryがないことを確認して返す."""
    if len(names) == 0:
        raise ValueError
    create_name = names[-1]
    parent, subs = fetch_subfolders(user_id, root, *names[:-1])
    if create_name in [s.name for s in subs if s is not None]:
        p = "/".join([root, *names])
        msg = f"/{p}'は既に存在しています"
        raise EntryAlreadyExistsError(msg)
    return parent


def create_sub_folder(user_id: UUIDy, root: str, *names: str) -> LFolder:
    """サブフォルダ作成(同配下に名前の重複がないことを確認)."""
    parent = check_and_get_parent(user_id, root, *names)
    sub = LFolder(name=names[-1]).save()
    sub.parent.connect(parent)
    return sub


def create_sub_resource(
    user_id: UUIDy,
    root: str,
    *names: str,
    authors: list[str] | None = None,
    published: date | None = None,
    urls: list[str] | None = None,
) -> LResource:
    """フォルダ配下に作成."""
    parent = check_and_get_parent(user_id, root, *names)
    d = {
        "name": names[-1],
        "authors": authors,
        "published": published,
        "urls": urls,
    }
    r = LResource(**d).save()
    r.parent.connect(parent)
    return r


def fetch_subfolders(
    user_id: UUIDy,
    root: str,
    *names: str,
) -> tuple[LFolder, tuple[LFolder]]:
    """ネットワークを辿ってフォルダとその配下をピンポイントに取得."""
    n = len(names)
    uid = to_uuid(user_id)
    qs = [
        f"MATCH (:User {{uid: $uid}})<-[:OWNED]-(f0:Entry {{ name: '{root}' }})",
        *[
            f"<-[:PARENT]-(f{i+1}:Folder {{ name: '{name}' }})"
            for i, name in enumerate(names)
        ],
        f"OPTIONAL MATCH (f{n})<-[:PARENT]-(sub:Entry)",
        f"RETURN f{n}, sub",
    ]
    q = "\n".join(qs)
    res = db.cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )[0]  # 1要素の2重リスト[[...]]のはず
    if len(res) == 0:
        p = "/".join([root, *names])
        msg = f"フォルダ'/{p}'が見つからない"
        raise EntryNotFoundError(msg, res)

    targets, subs = zip(*res)
    return targets[0], subs


def fetch_namespace(user_id: UUIDy) -> NameSpace:
    """ユーザー配下のサブフォルダ."""
    q = """
        MATCH (user:User {uid: $uid})
        OPTIONAL MATCH (user)<-[:OWNED]-(root:Entry)
        RETURN root as f1, null as f2
        UNION
        OPTIONAL MATCH (root)<-[:PARENT]-(sub:Entry)
        RETURN root as f1, sub as f2
        UNION
        OPTIONAL MATCH (sub)<-[:PARENT]-+(f1:Folder)<-[:PARENT]-(f2:Entry)
        RETURN f1, f2
    """
    uid = to_uuid(user_id)
    res = db.cypher_query(q, params={"uid": uid.hex}, resolve_objects=True)
    g = nx.DiGraph()
    roots = {}
    for f1, f2 in res[0]:
        if f2 is None:
            if f1 is not None:
                root_lb = f1.frozen
                roots[f1.name] = root_lb
                g.add_node(root_lb)
            continue
        m1 = f1.frozen
        m2 = f2.frozen
        g.add_edge(m1, m2)
    return NameSpace(roots_=roots, g=g, user_id=uid)


def move_folder(user_id: UUIDy, target: PurePath | str, to: PurePath | str) -> LFolder:
    """フォルダの移動(配下ごと)."""
    target = PurePath(target)  # PathはOSのファイルシステムを参照するらしく不適
    to = PurePath(to)
    if not (target.is_absolute() and to.is_absolute()):
        msg = "絶対パスで指定して"
        raise ValueError(msg, target, to)
    fs = fetch_namespace(user_id)
    tgt = LFolder(**fs.get(*target.parts[1:]).model_dump())
    tgt.parent.disconnect(tgt.parent.get())
    to_names = to.parts[1:]
    if len(to_names) == 0:  # rootへ
        luser = LUser.nodes.get(uid=user_id)
        tgt.owner.connect(luser)
        return tgt
    parent_to_move = LFolder(**fs.get(*to_names[:-1]).model_dump())
    tgt.parent.connect(parent_to_move)
    tgt.name = to_names[-1]
    return tgt.save()


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
