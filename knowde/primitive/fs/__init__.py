"""file system."""
from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any, Callable, TypeAlias

from pydantic import BaseModel
from typing_extensions import override

_DIR_PATH = Path.home() / ".config" / "knowde"


@cache
def dir_path() -> Path:
    """ファイル保管用ディレクトリ."""
    _DIR_PATH.mkdir(parents=True, exist_ok=True)
    return _DIR_PATH


# 変更があればTrue
DiffDiscriminator: TypeAlias = Callable[[str, str], bool]


def _dis(s1: str, s2: str) -> bool:
    return s1 != s2


class Versioning(BaseModel):
    """ファイルのバージョン."""

    name: str  # id
    root_dir: Path
    dis: DiffDiscriminator = _dis

    @property
    def _path(self) -> Path:
        return self.root_dir / self.name

    @override
    def model_post_init(self, __context: Any) -> None:
        """同一対象を収める用のディレクトリを作成."""
        self._path.mkdir(parents=True, exist_ok=True)

    @property
    def versions(self) -> list[Path]:
        """順番にソートして返す."""
        return list(self._path.iterdir())

    @property
    def latest(self) -> int:
        """最新バージョン."""
        return len(self.versions)

    def add(self, txt: str) -> None:
        """変更があった場合に保存."""
        pre = self._path / str(self.latest - 1)
        if pre.exists():
            prev_txt = pre.read_text()
            # 前versionから変更なし
            if not self.dis(prev_txt, txt):
                return
        p = self._path / str(self.latest)
        p.write_text(txt)

    def size_kb(self) -> int:
        """容量[MB]."""
        s_byte = 0
        for v in self.versions:
            s_byte += v.stat().st_size
        return s_byte // 1024  # B -> kiB
