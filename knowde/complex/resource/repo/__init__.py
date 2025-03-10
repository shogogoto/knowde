"""resource repository."""
from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

from pydantic import RootModel

from knowde.complex.resource import ResourceMeta
from knowde.complex.resource.category.folder import MFolder, MResource, NameSpace
from knowde.complex.resource.label import LFolder, LResource

if TYPE_CHECKING:
    from knowde.primitive.user.repo import LUser


class SyncResourceMeta(RootModel[list[ResourceMeta]]):
    """リクエスト用."""


def save_resource(m: ResourceMeta, ns: NameSpace, u: LUser) -> LResource | None:
    """新規作成 or 更新."""
    path = ns.get_path(*m.names)
    head = next((p for p in reversed(path) if p is not None), None)
    match head:
        case None:  # 新規作成
            lb = LResource(**m.model_dump()).save()
            if len(m.names) == 1:  # root file
                lb.owner.connect(u)
            else:
                folders = LFolder.create(*[{"name": name} for name in m.names[:-1]])
                folders[0].owner.connect(u)
                for f1, f2 in pairwise(folders):
                    f2.parent.connect(f1)
                lb.parent.connect(folders[-1])
            return lb
        case MFolder():  # フォルダが既存
            i = path.index(head)  # not none の最初の位置
            folders = LFolder.create(*[{"name": name} for name in m.names[i + 1 : -1]])
            parents = [LFolder(**head.model_dump()), *folders]
            for f1, f2 in pairwise(parents):
                f2.parent.connect(f1)
            lb = LResource(**m.model_dump()).save()
            lb.parent.connect(parents[-1])
            return lb
        case MResource():  # 更新
            if m.txt_hash == head.txt_hash:  # 変更なし
                return None
            lb = LResource(**head.model_dump())
            for k, v in m.model_dump().items():
                setattr(lb, k, v)
            return lb.save()
        case _:
            raise ValueError


# def sync_namespace(user_id: UUIDy, meta: SyncResourceMeta) -> NameSpace:
#     """名前空間の同期."""
#     ns = fetch_namespace(user_id)
#     print(ns)


# def should_update_entries(user_id: UUID, meta: SyncResourceMeta) -> None:
#     """更新すべきリソースを返す."""
