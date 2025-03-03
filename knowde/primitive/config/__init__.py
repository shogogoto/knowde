"""file system."""
from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Annotated, Any, Callable, Final, Self, TypeAlias, TypedDict

from pydantic import BaseModel, PlainSerializer
from typing_extensions import override

CONFIG_PATH: Final = Path.home() / ".config" / "knowde"


@cache
def dir_path() -> Path:
    """ファイル保管用ディレクトリ."""
    CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    return CONFIG_PATH


CONFIG_FILE: Final = dir_path() / "config.json"


class Credential(TypedDict):
    """認証情報."""

    access_token: str
    token_type: str


class LocalConfig(BaseModel):
    """設定ファイル."""

    LINK: Annotated[
        Path | None,
        PlainSerializer(lambda x: str(x), return_type=str, when_used="json"),
    ] = None

    CREDENTIALS: Credential | None = None

    @classmethod
    def load(cls) -> Self:
        """読み取り."""
        data = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
        return cls.model_validate(data)

    def save(self) -> None:
        """書き込み."""
        CONFIG_FILE.write_text(self.model_dump_json(indent=2))


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
