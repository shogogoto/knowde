"""共通DBクエリ関連."""

from pydantic import BaseModel, Field


class Paging(BaseModel):
    """クエリのページング."""

    page: int = Field(default=1, gt=0)
    size: int = Field(default=100, gt=0)

    @property
    def skip(self) -> int:  # noqa: D102
        return (self.page - 1) * self.size

    def phrase(self) -> str:
        """1ページから始まる."""
        return f"""
        SKIP {self.skip} LIMIT {self.size}
        """
