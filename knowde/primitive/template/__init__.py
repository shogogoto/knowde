"""文字列で文字列を返す関数を生成."""
from __future__ import annotations

from typing import Annotated, Final, NoReturn, Self

from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, model_validator

from knowde.primitive.__core__.dupchk import DuplicationChecker
from knowde.primitive.term.const import Marker

from .errors import (
    InvalidTemplateNameError,
    TemplateArgMismatchError,
    TemplateConflictError,
    TemplateNotFoundError,
    TemplateUnusedArgError,
)

SEP_TMPL: Final = ":"
ANGLE_MARKER: Final = Marker(m_open="<", m_close=">")  # 山括弧
ARG_SEP_TMPL: Final = ","

CALL_MARKER: Final = Marker(m_open="`", m_close="`")


def valid_name(value: str) -> str:
    """テンプレート名validation."""
    if ANGLE_MARKER.contains(value):
        msg = f"テンプレート名'{value}'にマークが含まれています"
        raise InvalidTemplateNameError(msg)
    return value.strip()


def get_template_name(first: str) -> str:
    """区切り前半からテンプレート名."""
    pre = first.rsplit(ANGLE_MARKER.m_open, maxsplit=1)[0]
    return valid_name(pre)  # argより先にチェック


def get_template_args(first: str) -> list[str]:
    """区切り前半から引数."""
    args = []
    for m in ANGLE_MARKER.pick(first):
        args.extend([s.strip() for s in m.split(ARG_SEP_TMPL)])
    return args


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
        return cls(
            name=get_template_name(first),
            args=get_template_args(first),
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

    @property
    def is_nested(self) -> bool:
        """formにテンプレートを含むか."""
        return CALL_MARKER.contains(self.form)


def template_dup_checker() -> DuplicationChecker:
    """テンプレート重複チェッカー."""

    def _err(t: Template) -> NoReturn:
        msg = f"テンプレート名'{t}'が重複しています"
        raise TemplateConflictError(msg)

    return DuplicationChecker(err_fn=_err)


def get_template_signature(line: str) -> list:
    """テンプレート名と引数の入れ子を含む文字列を分解."""
    sig = []
    pre, _ = line.split(ANGLE_MARKER.m_open, maxsplit=1)
    _, post = line.split(pre, maxsplit=1)
    name = pre.strip()
    for m in ANGLE_MARKER.pick_nesting(post):
        sp = [s.strip() for s in m.split(ARG_SEP_TMPL)]
        idxs = [i for i, s in enumerate(sp) if ANGLE_MARKER.contains(s)]
        if len(idxs) == 0:
            sig.extend([name, sp])
        else:
            imin = min(idxs)
            imax = max(idxs)
            contained = ARG_SEP_TMPL.join(sp[imin : imax + 1])
            args = sp[:imin] + [get_template_signature(contained)] + sp[imax + 1 :]
            sig.extend([name, args])
    return sig


# formにテンプレがあるか
#  あるならそれを展開する
#  入れ子対応
# atom templates is not nested から始めて
class Templates(BaseModel):
    """テンプレートのあつまり."""

    values: list[Template] = Field(default_factory=list)
    _chk: DuplicationChecker = PrivateAttr(default_factory=template_dup_checker)

    def add(self, *ts: Template) -> Self:
        """templateを重複なく追加."""
        for t in ts:
            self._chk(t.name)
            self.values.append(t)
        return self

    def format(self, t: Template, *args: str) -> str:
        """formにあるテンプレを展開する."""
        if t not in self.values:
            msg = f"'{t.name}テンプレートは存在しません'"
            raise TemplateNotFoundError(msg, t)

        return t.format(*args)
        # print("form:", s)
        # called = CALL_MARKER.pick_nesting(s)

        # for cl in called:
        #     print("call", cl)
        #     for m in ANGLE_MARKER.pick_nesting(cl):
        #         print(get_template_signature(m))

        # for name, _args in get_nested(s):
        #     print(name, _args)
        #     _t = self.get(name)
        #     repl = self.format(_t, *_args) if _t.is_nested else _t.format(*_args)
        #     s = CALL_MARKER.replace(s, repl)

    def get(self, name: str) -> Template:
        """Get template from name."""
        ls = [t for t in self.values if t.name == name]
        match len(ls):
            case 0:
                msg = f"'{name}テンプレートは存在しません'"
                raise TemplateNotFoundError(msg)
            case 1:
                return ls[0]
            case _:
                msg = f"テンプレート'{name}'が複数あります"
                raise TemplateConflictError(msg, ls)
