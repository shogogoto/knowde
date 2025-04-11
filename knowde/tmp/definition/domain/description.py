"""mark関連関数をクラスにまとめたもの."""

from __future__ import annotations

from pydantic import BaseModel, Field

from knowde.tmp.definition.domain.mark import (
    MARK_CLOSE,
    MARK_OPEN,
    inject2placeholder,
    mark2placeholder,
    pick_marks,
)


class MarkValue(BaseModel, frozen=True):
    """マークの中身."""

    value: str


class Description(BaseModel, frozen=True):
    """markが埋め込まれた説明文."""

    value: str = Field(description="置換前説明文")

    @property
    def markvalues(self) -> list[MarkValue]:
        """markの値一覧."""
        return [MarkValue(value=v) for v in pick_marks(self.value)]

    @property
    def placeheld(self) -> PlaceHeldDescription:
        """プレースホルダー置換後の説明文."""
        v = mark2placeholder(self.value)
        return PlaceHeldDescription(value=v)


class PlaceHeldDescription(BaseModel, frozen=True):
    """プレースホルダー置換後の説明文.

    DBに格納される側
    """

    value: str

    def inject(
        self,
        values: list[str],
    ) -> Description:
        """プレースホルダーを置換."""
        v = inject2placeholder(self.value, values, prefix=MARK_OPEN, suffix=MARK_CLOSE)
        return Description(value=v)
