"""同期."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Iterable

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.resource.nx2db.save import resource_meta
from knowde.complex.resource.router import ResourceMetas
from knowde.primitive.__core__.timeutil import TZ

if TYPE_CHECKING:
    from pathlib import Path

    from knowde.complex.resource import ResourceMeta


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


def path2meta(
    anchor: Path,
    paths: Iterable[Path],
    show_error: bool = False,  # noqa: FBT001 FBT002
) -> ResourceMetas:
    """ファイルをメタ情報へ変換."""
    data = ResourceMetas(root=[])
    for p in paths:
        if not can_parse(p, show_error):
            continue
        meta = read_meta(p, anchor)
        data.root.append(meta)
    return data


def read_meta(p: Path, anchor: Path) -> ResourceMeta:
    """ファイルのメタ情報を取得."""
    s = p.read_text()
    st = p.stat().st_mtime  # 最終更新日時
    t = datetime.fromtimestamp(st, tz=TZ)  # JST が neo4jに対応してないみたいでエラー
    sn = parse2net(s)
    meta = resource_meta(sn)
    meta.updated = t
    meta.txt_hash = hash(s)  # ファイルに変更があったかをhash値で判断
    meta.path = p.relative_to(anchor).parts
    return meta
