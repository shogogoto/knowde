"""文字列で文字列を返す関数を生成."""
from __future__ import annotations

import re
from functools import cache, cached_property
from typing import Annotated, Final, NoReturn, Self

from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, model_validator
from regex import regex

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

CALL_MARKER: Final = Marker(m_open="_", m_close="_")


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


def get_template_args(first: str) -> tuple[str]:
    """区切り前半から引数."""
    args = []
    for m in ANGLE_MARKER.pick(first):
        args.extend([s.strip() for s in m.split(ARG_SEP_TMPL)])
    return tuple(args)


class Template(BaseModel, frozen=True):
    """文字列から生成される文字列関数."""

    name: Annotated[str, Field(min_length=1), AfterValidator(valid_name)]
    args: tuple[str, ...]
    form: str

    @model_validator(mode="after")
    def valid_use_arg(self) -> Self:  # noqa: D102
        unused = [a for a in self.args if a not in self.form]
        if len(unused) > 0:
            msg = f"未使用のテンプレート引数{unused}が定義されています"
            raise TemplateUnusedArgError(msg, self.form)
        return self

    @classmethod
    def is_parsable(cls, line: str) -> bool:
        """パース対象とな文字列か判定."""
        if SEP_TMPL not in line:
            return False
        first, _ = line.split(SEP_TMPL, maxsplit=1)
        return ANGLE_MARKER.contains(first) and ANGLE_MARKER.is_pickable(first)

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
        a = ANGLE_MARKER.enclose(a)
        sig = f"{self.name}{a}"
        return f"{sig}: {self.form}"

    def __repr__(self) -> str:  # noqa: D105
        return str(self)

    @property
    def is_nested(self) -> bool:
        """formにテンプレートを含むか."""
        return CALL_MARKER.contains(self.form)

    @cached_property
    def _pattern(self) -> regex.Pattern:
        """f<...>の...を抽出するパターン."""
        ao = ANGLE_MARKER.m_open
        ac = ANGLE_MARKER.m_close
        o = f"{self.name}{ao}"
        c = ac
        return regex.compile(rf"{ao}((?:[^{o}{ac}]++|(?R))*){c}")

    def pick_marked(self, s: str) -> list[str]:
        """`f<...>`を抽出."""
        return self._pattern.findall(s)

    def enclose(self, s: str) -> str:
        """テンプレ呼び出しで囲む."""
        o = f"{self.name}{ANGLE_MARKER.m_open}"
        c = ANGLE_MARKER.m_close
        return f"{o}{s}{c}"

    def apply(self, s: str, *argstpls: list[str]) -> str:
        """文字列てプレートを適用して返す."""
        txt = s
        for m, args in zip(self.pick_marked(s), argstpls, strict=True):
            f = self.format(*args)
            txt = txt.replace(self.enclose(m), f)
        return txt

    def embedded_args(self, s: str) -> list[list[str]]:
        """文字列に埋め込まれた引数."""
        p = _embedded_pattern()
        return [p.split(m) for m in self.pick_marked(s)]


def split_for_args(s: str) -> list[str]:
    """括弧(){}[]<>で囲まれた部分を無視してsplit."""
    return _embedded_pattern().split(s)


@cache
def _embedded_pattern() -> re.Pattern:
    pattern = rf"{ARG_SEP_TMPL}(?![^{{\[\(\<]*[\]}}\)\>])"
    return re.compile(pattern)


def get_template_signature(line: str) -> list:
    """テンプレート名と引数の入れ子を含む文字列を分解."""
    sig = []
    pre, _ = line.split(ANGLE_MARKER.m_open, maxsplit=1)
    _, post = line.split(pre, maxsplit=1)
    name = pre.strip()
    for m in ANGLE_MARKER.pick_nesting(post):
        sp = [s.strip() for s in split_for_args(m) if s.strip() != ""]
        args = [
            get_template_signature(s) if ANGLE_MARKER.contains(s) else s for s in sp
        ]
        sig.extend([name, args])
    return sig


# formにテンプレがあるか
#  あるならそれを展開する
#  入れ子対応
# atom templates is not nested から始めて


def template_dup_checker() -> DuplicationChecker:
    """テンプレート重複チェッカー."""

    def _err(t: Template) -> NoReturn:
        msg = f"テンプレート名'{t}'が重複しています"
        raise TemplateConflictError(msg)

    return DuplicationChecker(err_fn=_err)


class Templates(BaseModel):
    """テンプレートのあつまり."""

    _values: list[Template] = PrivateAttr(default_factory=list)
    _chk: DuplicationChecker = PrivateAttr(default_factory=template_dup_checker)

    def add(self, *ts: Template) -> Self:
        """templateを重複なく追加."""
        # 名前の重複を許さないためにvalues fieldを別途用意
        for t in ts:
            self._chk(t.name)
            self._values.append(t)
        return self

    def format(self, t: Template, *args: str) -> str:
        """formにあるテンプレを展開する."""
        self._contains(t)
        s = t.format(*args)  # 対象のargを適用
        called = CALL_MARKER.pick_nesting(s)  # その中からcall部分を列挙
        for cl in called:
            sig = get_template_signature(cl)
            v = self.apply(cl, sig)
            old = CALL_MARKER.enclose(cl)
            s = s.replace(old, v)
        return s.replace(CALL_MARKER.m_open, "")

    def apply(self, txt: str, args: list) -> str:
        """テンプレ名、引数リストを元にtxtにテンプレを適用."""
        # [tmpl_name, [tmpl_name, [...,args]]]
        if len(args) != 2:  # noqa: PLR2004
            raise ValueError
        t = self.get(args[0])
        tmpl_args = args[1]
        if len(tmpl_args) == 0:  # 引数なしはそのまま返す
            return txt
        match tmpl_args[0]:
            case str():  # これ以上入れ子がない
                return t.apply(txt, tmpl_args)
            case list():
                vs = [self.apply(m, tmpl_args[0]) for m in t.pick_marked(txt)]
                return self.format(t, *vs)
            case _:
                raise ValueError

    def get(self, name: str) -> Template:
        """Get template from name."""
        ls = [t for t in self._values if t.name == name]
        match len(ls):
            case 0:
                msg = f"'{name}テンプレートは存在しません'"
                raise TemplateNotFoundError(msg)
            case 1:
                return ls[0]
            case _:
                msg = f"テンプレート'{name}'が複数あります"
                raise TemplateConflictError(msg, ls)

    def _contains(self, t: Template) -> None:
        if t not in self._values:
            msg = f"'{t.name}テンプレートは存在しません'"
            raise TemplateNotFoundError(msg, t)
