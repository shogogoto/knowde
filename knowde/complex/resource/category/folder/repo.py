"""floder DB."""
from __future__ import annotations

from typing import TypeAlias
from uuid import UUID

from neomodel import (
    INCOMING,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    Traversal,
    UniqueIdProperty,
    ZeroOrOne,
    db,
)

from knowde.complex.resource.category.folder.errors import (
    FolderAlreadyExistsError,
    SubFolderCreateError,
)
from knowde.primitive.user.repo import LUser


class LFolder(StructuredNode):
    """sysnetの入れ物."""

    __label__ = "Folder"
    name = StringProperty(index=True)

    parent = RelationshipTo("LFolder", "PARENT", cardinality=ZeroOrOne)
    owner = RelationshipTo("LUser", "OWNED", cardinality=ZeroOrOne)


UUIDy: TypeAlias = UUID | str | UniqueIdProperty  # Falsyみたいな


def to_uuid(uidy: UUIDy) -> UUID:
    """neomodelのuid propertyがstrを返すからUUIDに補正・統一して扱いたい."""
    return UUID(uidy) if isinstance(uidy, (str, UniqueIdProperty)) else uidy


def create_folder(_user_id: UUIDy, *names: str) -> LFolder:
    """一般化フォルダ作成."""
    if len(names) == 0:
        msg = "フォルダ名を1つ以上指定して"
        raise ValueError(msg)


def create_root_folder(user_id: UUIDy, name: str) -> LFolder:
    """直下フォルダ作成."""
    u: LUser = LUser.nodes.get(uid=to_uuid(user_id).hex)
    _f = LFolder.nodes.get_or_none(name=name)
    if _f is not None:
        raise FolderAlreadyExistsError
    f: LFolder = LFolder(name=name).save()
    f.owner.connect(u)
    return f


def create_sub_folder(user_id: UUIDy, *path: str) -> None:
    """サブフォルダ作成."""
    n = len(path)
    if n <= 1:
        msg = "parent, subの2つ以上の文字列が必要"
        raise ValueError(msg)
    uid = to_uuid(user_id)
    first = path[0]

    q0 = f"MATCH (:User {{uid: $uid}})<-[:OWNED]-(f0:Folder {{ name: '{first}' }})"
    qs = [
        f"<-[:PARENT]-(f{i+1}:Folder {{ name: '{name}' }})"
        for i, name in enumerate(path[1:-1])
    ]
    i_parent = n - 2
    qsub = f"OPTIONAL MATCH (f{i_parent})<-[:PARENT]-(sub:Folder)"
    qe = f"RETURN f{i_parent}, sub"

    q = "\n".join([q0, *qs, qsub, qe])

    res = db.cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )[0]  # 1要素の2重リスト[[...]]のはず
    if len(res) != 1:
        p = "/".join(path[:-1])
        msg = f"親フォルダ'/{p}'が見つからない"
        raise SubFolderCreateError(msg, res)
    parent, sub = res[0]
    if sub is not None and sub.name == path[-1]:
        p = "/".join(path)
        msg = f"サブフォルダ'/{p}'が既に存在している"
        raise FolderAlreadyExistsError(msg)
    sub = LFolder(name=path[-1]).save()
    sub.parent.connect(parent)
    return sub


def fetch_root_folders(user_id: UUIDy) -> list[LFolder]:
    """直下フォルダ."""
    return Traversal(
        LUser.nodes.get(uid=to_uuid(user_id).hex),
        "Folder",
        {"node_class": LFolder, "direction": INCOMING, "relation_type": "OWNED"},
    ).all()


def fetch_folders(user_id: UUIDy) -> None:
    """配下のフォルダ."""
    q = """
        MATCH (user:User {uid: $uid})
        OPTIONAL MATCH (user)<-[:OWNED]-(root:Folder)
        OPTIONAL MATCH (root)<-[:PARENT]-(sub:Folder)
        RETURN root as f1, sub as f2
        UNION
        OPTIONAL MATCH (sub)<-[:PARENT]-*(f1:Folder)<-[:PARENT]-(f2:Folder)
        RETURN f1, f2
    """
    uid = to_uuid(user_id)
    _res = db.cypher_query(q, params={"uid": uid.hex})
    # for f1, f2 in res[0]:
    #     print("-" * 30)
    #     print(f1, f2)
