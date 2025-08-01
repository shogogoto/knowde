"""file system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Final, Self

from pydantic import BaseModel, PlainSerializer
from typing_extensions import TypedDict

from knowde.config.env import Settings

s = Settings()
_F: Final = s.config_file


class Credential(TypedDict):
    """認証情報."""

    access_token: str
    token_type: str


class LocalConfig(BaseModel):
    """設定ファイル."""

    ANCHOR: Annotated[
        Path | None,
        PlainSerializer(str, return_type=str, when_used="json"),
    ] = None

    CREDENTIALS: Credential | None = None

    @classmethod
    def load(cls) -> Self:
        """読み取り."""
        data = json.loads(_F.read_text()) if _F.exists() else {}
        return cls.model_validate(data)

    def save(self) -> None:
        """書き込み."""
        _F.write_text(self.model_dump_json(indent=2))
