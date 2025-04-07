"""同期."""

from __future__ import annotations  # noqa: I001

from datetime import datetime

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.entry import ResourceMeta
from knowde.complex.entry.router import ResourceMetas
from knowde.primitive.__core__.timeutil import TZ

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
        parse2net(p.read_text())
    except Exception as e:  # noqa: BLE001
        if handle_error is not None:
            handle_error(p, e)
        return False
    return True


def filter_parsable(
    *ps: Path,
    handle_error: ParseHandler | None = None,
) -> list[Path]:
    """パースできるファイルのみを抽出."""
    return [p for p in ps if can_parse(p, handle_error)]


def txt2meta(s: str) -> ResourceMeta:
    """テキストをメタ情報へ変換."""
    sn = parse2net(s)
    meta = ResourceMeta.of(sn)
    meta.txt_hash = hash(s)  # ファイルに変更があったかをhash値で判断
    return meta


def read_meta(p: Path, anchor: Path) -> ResourceMeta:
    """ファイルのメタ情報を取得."""
    st = p.stat().st_mtime  # 最終更新日時
    t = datetime.fromtimestamp(st, tz=TZ)  # JST が neo4jに対応してないみたいでエラー
    meta = txt2meta(p.read_text())
    meta.updated = t
    meta.path = p.relative_to(anchor).parts
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
        meta = txt2meta(p.read_text())
        meta.updated = t
        meta.path = p.relative_to(self).parts
        return meta

    def to_metas(self, ps: Iterable[Path]) -> ResourceMetas:
        """テキストファイル群からメタ情報群へ."""
        data = ResourceMetas(root=[])
        for p in ps:
            meta = self.to_meta(p)
            data.root.append(meta)
        return data
