"""文字列で文字列を返す関数を生成."""
from __future__ import annotations

from typing import Annotated, Final, Self

from pydantic import AfterValidator, BaseModel, Field, model_validator

from knowde.primitive.term.const import Marker

from .errors import (
    InvalidTemplateNameError,
    TemplateArgMismatchError,
    TemplateUnusedArgError,
)

SEP_TMPL: Final = ":"
ANGLE_MARKER: Final = Marker(m_open="<", m_close=">")  # 山括弧
ARG_SEP_TMPL: Final = ","


def valid_name(value: str) -> str:
    """テンプレート名validation."""
    if ANGLE_MARKER.contains(value):
        msg = f"テンプレート名'{value}'にマークが含まれています"
        raise InvalidTemplateNameError(msg)
    return value.strip()


class Template(BaseModel, frozen=True):
    """文字列から生成される文字列関数."""

    name: Annotated[str, Field(min_length=1), AfterValidator(valid_name)]
    args: list[str]
    form: str

    @model_validator(mode="after")
    def valid_use_arg(self) -> Self:  # noqa: D102
        unused = [a for a in self.args if a not in self.form]
        if len(unused) > 0:
            msg = f"未使用のテンプレート引数{unused}が定義されています"
            raise TemplateUnusedArgError(msg, self.form)
        return self

    @classmethod
    def parse(cls, line: str) -> Self:
        """文字列をパースしてTemplateを生成."""
        txt = line.strip()
        first, second = txt.split(SEP_TMPL, maxsplit=1)
        pre = first.rsplit(ANGLE_MARKER.m_open, maxsplit=1)[0]
        valid_name(pre)  # argより先にチェック
        args = []
        for m in ANGLE_MARKER.pick(first):
            args.extend([s.strip() for s in m.split(ARG_SEP_TMPL)])

        return cls(
            name=pre,
            args=args,
            form=second.strip(),
        )

    def format(self, *args: str) -> str:
        """出力する."""
        if len(self.args) != len(args):
            msg = f"テンプレート引数が不整合です{self.args}, {args}"
            raise TemplateArgMismatchError(msg)
        ret = self.form
        for old, new in zip(self.args, args, strict=True):
            ret = ret.replace(old, new)
        return ret

    def __str__(self) -> str:  # noqa: D105
        a = ", ".join(self.args)
        return f"{self.name}<{a}>: {self.form}"
