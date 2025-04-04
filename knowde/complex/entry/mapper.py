"""neomodelのhashableな表現."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic_core import Url


class Entry(BaseModel, frozen=True):
    """namespace用のhashableな表現."""

    name: str  # = Field(alias="title")
    element_id_property: str | None = None
    uid: UUID


class MFolder(Entry, frozen=True):
    """LFolderのgraph用Mapper."""

    def __str__(self) -> str:
        """Prefix / でフォルダであることを明示."""
        return f"/{self.name}"


class MResource(Entry, frozen=True):
    """LResourceのOGM, リソースのメタ情報."""

    authors: frozenset[str] | None = None
    published: date | None = None
    urls: frozenset[Url] | None = None

    # ファイル由来
    path: tuple[str, ...] | None = None
    updated: datetime | None = None
    txt_hash: int | None = None

    def __str__(self) -> str:
        """For display."""
        return self.name
