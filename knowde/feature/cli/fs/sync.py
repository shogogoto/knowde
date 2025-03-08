"""同期."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.resource.nx2db.save import resource_meta
from knowde.primitive.__core__.timeutil import TZ

if TYPE_CHECKING:
    from pathlib import Path

    from knowde.complex.resource.nx2db.save import ResourceMeta


def can_parse(p: Path, show_error: bool) -> bool:  # noqa: FBT001
    """エラーなくパースできるか."""
    if not p.is_file():
        return False
    try:
        parse2net(p.read_text())
    except Exception as e:  # noqa: BLE001
        print(f"'{p}'のパースに失敗")  # noqa: T201
        if show_error:
            print("    ", e)  # noqa: T201
        return False
    return True


def read_meta(p: Path) -> ResourceMeta:
    """ファイルのメタ情報を取得."""
    s = p.read_text()
    st = p.stat().st_mtime  # 最終更新日時
    t = datetime.fromtimestamp(st, tz=TZ)
    sn = parse2net(s)
    meta = resource_meta(sn)
    meta.updated = t
    meta.txt_hash = hash(s)  # ファイルに変更があったかをhash値で判断
    return meta
