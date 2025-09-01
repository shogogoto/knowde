"""同期."""

from __future__ import annotations  # noqa: I001

from datetime import datetime

from knowde.feature.parsing.tree2net import parse2net
from knowde.feature.entry import ResourceMeta
from knowde.feature.entry.router import ResourceMetas
from knowde.shared.util import TZ

from pathlib import Path

from collections.abc import Callable, Iterable

type ParseHandler = Callable[[Path, Exception], None]


def can_parse(
    p: Path,
    handle_error: ParseHandler | None = None,
) -> bool:
    """エラーなくパースできるか."""
    if not p.is_file():
        return False
    try:
        parse2net(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        if handle_error is not None:
            handle_error(p, e)
        return False
    return True


def filter_parsable(
    handle_error: ParseHandler | None = None,
) -> Callable[[Iterable[Path]], list[Path]]:
    """パースできるファイルのみを抽出."""

    def _f(_ps: Iterable[Path]) -> list[Path]:
        return [p for p in _ps if can_parse(p, handle_error)]

    return _f


def txt2meta(s: str) -> ResourceMeta:
    """テキストをメタ情報へ変換."""
    sn = parse2net(s)
    meta = ResourceMeta.of(sn)
    meta.txt_hash = hash(s)  # ファイルに変更があったかをhash値で判断
    return meta


class Anchor(Path):
    """動悸するファイルシステムのルート."""

    def to_meta(
        self,
        p: Path,
    ) -> ResourceMeta:
        """テキストファイルからメタ情報へ."""
        st = p.stat().st_mtime  # 最終更新日時
        t = datetime.fromtimestamp(st, tz=TZ)  # JST が neo4jに非対応
        meta = txt2meta(p.read_text(encoding="utf-8"))
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
