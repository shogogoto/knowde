"""sysnetの管理.

モチベは?
userId/folder
    CRUD

    root folder user直下
    folder は 配下ではnameが重複してはならない
    rename
    remove 配下のフォルダとsysnetも全て削除
    move parentを差し替える

    folderのCRUD
    folderとCLIのsync upload
        変更があったか否かを低コストでチェックできるとよい
            sysnet のhash値とか使える?

        find コマンドとの連携を考えるか
            自前で作らない方がいい

    folder と CLI userのディレクトリの同期
        CLI find して ファイルパスの構造をそのままsync(永続化)
          -> Git管理できて便利
"""
from __future__ import annotations

import networkx as nx
from pydantic import BaseModel, Field

from knowde.complex.resource.category.folder.mapper import MFolder  # noqa: TCH001
from knowde.primitive.__core__.types import NXGraph  # noqa: TCH001


class FolderSpace(BaseModel):
    """リソースの分類."""

    g: NXGraph = Field(default_factory=nx.DiGraph)
    roots_: dict[str, MFolder] = Field()

    def children(self, root: str, *path: str) -> list[str]:
        """element_idなしで文字列だけでアクセス."""
        r = self.roots_[root]
        succs = self.g.successors(r)
        for p in path:
            succs = [n for n in succs if str(n) == p]
            if len(succs) != 1:  # 存在しないパスに対して空を返す
                return []
            succs = self.g.successors(succs[0])
        return sorted([str(c) for c in succs])

    @property
    def roots(self) -> list[str]:
        """ユーザー直下のフォルダ一覧."""
        return list(self.roots_.keys())
