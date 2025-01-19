"""文字列で文字列を返す関数を生成."""
from __future__ import annotations

from typing import Final, Self

from pydantic import BaseModel, Field

from knowde.primitive.term.const import Marker

TMPL_SEP: Final = ":"
ANGLE_MARKER: Final = Marker(m_open="<", m_close=">")  # 山括弧


class Template(BaseModel, frozen=True):
    """文字列から生成される文字列関数."""

    name: str = Field(min_length=1)
    args: list[str]
    form: str

    @classmethod
    def parse(cls, line: str) -> Self:
        """文字列をパースしてTemplateを生成."""
        txt = line.strip()
        first, second = txt.split(TMPL_SEP, maxsplit=1)
        name = first.split(ANGLE_MARKER.m_open)[0]
        return cls(
            name=name.strip(),
            args=ANGLE_MARKER.pick(first),
            form=second.strip(),
        )

    def __call__(self, *args: str) -> str:  # noqa: D102
        ret = self.form
        for old, new in zip(self.args, args, strict=True):
            ret = ret.replace(old, new)
        return ret
