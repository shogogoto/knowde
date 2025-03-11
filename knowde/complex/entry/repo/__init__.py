"""resource repository."""
from __future__ import annotations

from itertools import pairwise
from typing import TypeAlias
from uuid import UUID

from pydantic import RootModel

from knowde.complex.entry import ResourceMeta
from knowde.complex.entry.category.folder import MFolder, MResource, NameSpace
from knowde.complex.entry.label import LFolder, LResource
from knowde.primitive.user.repo import LUser


class ResourceMetas(RootModel[list[ResourceMeta]]):
    """リクエスト用."""

    @property
    def titles(self) -> list[str]:  # noqa: D102
        return [r.title for r in self.root]


UpdateFileMap: TypeAlias = dict[tuple[str, ...], UUID]  # Path と resource id


def fill_parents(ns: NameSpace, *names: str) -> LFolder | None:
    """フォルダをDB上で繋げてtailを返す."""
    if len(names) == 0:
        return None
    path = ns.get_path(*names)
    tail = next((p for p in reversed(path) if p is not None), None)
    match tail:
        case None:  # 新規作成 = tail なし = 既存親なし
            u = LUser.nodes.get(uid=ns.user_id.hex)
            folders = LFolder.create(*[{"name": name} for name in names])
            head = folders[0]
            head.owner.connect(u)
            ns.add_root(head.frozen)
            for f1, f2 in pairwise(folders):
                f2.parent.connect(f1)
                ns.g.add_edge(f1.frozen, f2.frozen)
            return folders[-1]
        case MFolder():  # フォルダが途中まで既存
            i = path.index(tail) + 1  # not none の最初の位置
            folders = LFolder.create(*[{"name": name} for name in names[i:]])
            folders = [LFolder(**tail.model_dump()), *folders]
            for f1, f2 in pairwise(folders):
                f2.parent.connect(f1)
                ns.g.add_edge(f1.frozen, f2.frozen)
            return folders[-1]
        case _:
            raise ValueError


def save_resource(m: ResourceMeta, ns: NameSpace) -> LResource | None:
    """新規作成 or 更新して返す."""
    path = ns.get_path(*m.names)
    tail = next((p for p in reversed(path) if p is not None), None)
    match tail:
        case None | MFolder():  # 新規作成 or フォルダが途中まで既存
            lb = LResource(**m.model_dump()).save()
            parent = fill_parents(ns, *m.names[:-1])
            if parent is None:
                u = LUser.nodes.get(uid=ns.user_id.hex)
                lb.owner.connect(u)
            else:
                lb.parent.connect(parent)
            return lb
        case MResource():  # 更新
            if m.txt_hash == tail.txt_hash:  # 変更なし
                return None
            lb = LResource(**tail.model_dump())
            for k, v in m.model_dump().items():
                setattr(lb, k, v)
            return lb.save()
        case _:
            raise ValueError


def save_or_move_resource(m: ResourceMeta, ns: NameSpace) -> LResource | None:
    """移動を反映してsave."""
    old = next((r for r in ns.resources if r.name == m.title), None)
    if old is None:  # 新規
        return save_resource(m, ns)
    old = LResource(**old.model_dump()).save()
    new = fill_parents(ns, *m.names[:-1])
    old.parent.disconnect(old.parent.get())
    old.parent.connect(new)
    return old


def sync_namespace(metas: ResourceMetas, ns: NameSpace) -> UpdateFileMap:
    """変更や移動されたファイルパスとDB上のリソースの対応づける."""
    d = {}
    for m in metas.root:
        e = ns.get_or_none(*m.names)
        lb = save_or_move_resource(m, ns) if e is None else save_resource(m, ns)
        if lb is not None:
            d[m.names] = lb.uid
    return d
