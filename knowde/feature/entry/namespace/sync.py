"""同期."""

from __future__ import annotations  # noqa: I001

from datetime import datetime

from knowde.feature.entry.domain import ResourceMeta
from knowde.feature.entry.router import ResourceMetas
from knowde.feature.parsing.tree2net import filter_parsable
from knowde.shared.util import TZ

from pathlib import Path

from collections.abc import Callable, Iterable


class Anchor(Path):
    """動悸するファイルシステムのルート."""

    def to_meta(
        self,
        p: Path,
    ) -> ResourceMeta:
        """テキストファイルからメタ情報へ."""
        st = p.stat().st_mtime  # 最終更新日時
        t = datetime.fromtimestamp(st, tz=TZ)  # JST が neo4jに非対応
        meta, _sn = ResourceMeta.from_str(p.read_text(encoding="utf-8"))
        meta.updated = t
        meta.path = p.relative_to(self).parts
        return meta

    def to_metas(
        self,
        ps: Iterable[Path],
        filter_: Callable[[Iterable[Path]], list[Path]] = filter_parsable(),
    ) -> ResourceMetas:
        """テキストファイル群からメタ情報群へ."""
        data = ResourceMetas(root=[])
        for p in filter_(ps):
            meta = self.to_meta(p)
            data.root.append(meta)
        return data
