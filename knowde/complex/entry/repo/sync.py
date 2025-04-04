"""同期."""

from __future__ import annotations  # noqa: I001

from collections.abc import Iterable
from datetime import datetime

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.entry import ResourceMeta
from knowde.complex.entry.router import ResourceMetas
from knowde.primitive.__core__.timeutil import TZ

from pathlib import Path


def can_parse(p: Path, show_error: bool) -> bool:  # noqa: FBT001
    """エラーなくパースできるか."""
    if not p.is_file():
        return False
    try:
        parse2net(p.read_text())
    except Exception as e:  # noqa: BLE001
        if show_error:
            print(f"'{p}'のパースに失敗")  # noqa: T201
            print("    ", e)  # noqa: T201
        return False
    return True


def txt2meta(s: str) -> ResourceMeta:
    """テキストをメタ情報へ変換."""
    sn = parse2net(s)
    meta = ResourceMeta.of(sn)
    meta.txt_hash = hash(s)  # ファイルに変更があったかをhash値で判断
    return meta


def path2meta(
    anchor: Path,
    paths: Iterable[Path],
    show_message: bool = False,  # noqa: FBT001 FBT002
) -> ResourceMetas:
    """ファイルをメタ情報へ変換."""
    data = ResourceMetas(root=[])
    for p in paths:
        if show_message:
            print(p)  # noqa: T201
        if not can_parse(p, show_message):
            continue
        meta = read_meta(p, anchor)
        data.root.append(meta)
    return data


def read_meta(p: Path, anchor: Path) -> ResourceMeta:
    """ファイルのメタ情報を取得."""
    st = p.stat().st_mtime  # 最終更新日時
    t = datetime.fromtimestamp(st, tz=TZ)  # JST が neo4jに対応してないみたいでエラー
    meta = txt2meta(p.read_text())
    meta.updated = t
    meta.path = p.relative_to(anchor).parts
    return meta
