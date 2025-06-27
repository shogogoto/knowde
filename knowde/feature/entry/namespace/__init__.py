"""resource repository."""

from __future__ import annotations

from itertools import pairwise
from pathlib import Path

from pydantic import RootModel

from knowde.feature.entry import NameSpace, ResourceMeta
from knowde.feature.entry.errors import DuplicatedTitleError, SaveResourceError
from knowde.feature.entry.label import LFolder, LResource
from knowde.feature.entry.mapper import MFolder, MResource
from knowde.shared.labels.user import LUser


class ResourceMetas(RootModel[list[ResourceMeta]]):
    """リクエスト用."""

    def check_duplicated_title(self) -> None:
        """titleの重複を許さない."""
        titles = [m.title for m in self.root]
        if len(titles) != len(set(titles)):
            msg = "titleが重複しています"
            raise DuplicatedTitleError(msg, titles)


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
                ns.add_edge(f1.frozen, f2.frozen)
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
            if parent is None:  # user直下
                u = LUser.nodes.get(uid=ns.user_id.hex)
                lb.owner.connect(u)
                ns.add_root(lb.frozen)
            else:
                lb.parent.connect(parent)
                ns.add_edge(parent.frozen, lb.frozen)
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
    # NSに重複したタイトルがあると困る
    old = ns.get_resource_or_none(m.title)
    if old is None:  # 新規
        return save_resource(m, ns)
    ns.remove_resource(m.title)
    old = LResource(**old.model_dump()).save()  # reflesh
    owner = old.owner.get_or_none()
    parent = old.parent.get_or_none()
    if owner is None and parent is None:
        msg = "所有者も親もなかったなんてあり得ないからね"
        raise SaveResourceError(msg)
    if parent is None:  # owner直下
        old.owner.disconnect(owner)
    else:
        old.parent.disconnect(parent)
    new_parent = fill_parents(ns, *m.names[:-1])
    if new_parent is None:  # user直下
        u = LUser.nodes.get(uid=ns.user_id.hex)
        old.owner.connect(u)
        ns.add_root(old.frozen)
    else:
        old.parent.connect(new_parent)
        ns.add_edge(new_parent.frozen, old.frozen)
    return old


def sync_namespace(metas: ResourceMetas, ns: NameSpace) -> list[Path]:
    """変更や移動されたファイルパスをDBに反映して変更があったものを返す."""
    metas.check_duplicated_title()
    ls = []
    for m in metas.root:
        e = ns.get_or_none(*m.names)
        lb = save_or_move_resource(m, ns) if e is None else save_resource(m, ns)
        if lb is not None:
            ls.append(Path().joinpath(*m.path))
    return ls
