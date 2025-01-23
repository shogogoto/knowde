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
    name = value.strip()
    if len(name) == 0:
        msg = "テンプレート名が空です"
        raise InvalidTemplateNameError(msg, value)
    return name


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


@cache
def _template_pattern() -> re.Pattern:
    p = r"[^\<\>]+\<.*\>\s*:.+"
    return re.compile(p)


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
        return _template_pattern().match(line) is not None

    @classmethod
    def parse(cls, line: str) -> Self:
        """文字列をパースしてTemplateを生成."""
        first, second = line.split(SEP_TMPL, maxsplit=1)
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


def nested_tmpl_name_args(line: str) -> list:
    """テンプレート名と引数の入れ子を含む文字列を分解."""
    sig = []
    pre, _ = line.split(ANGLE_MARKER.m_open, maxsplit=1)
    _, post = line.split(pre, maxsplit=1)
    name = pre.strip()
    for m in ANGLE_MARKER.pick_nesting(post):
        sp = [s.strip() for s in split_for_args(m) if s.strip() != ""]
        args = [nested_tmpl_name_args(s) if ANGLE_MARKER.contains(s) else s for s in sp]
        sig.extend([name, args])
    return sig


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

    def apply(self, args: list) -> str:
        """名前、引数の入れ子からformat."""
        if len(args) != 2:  # noqa: PLR2004
            raise ValueError
        t = self.get(args[0])
        tmpl_args = args[1]
        match tmpl_args[0]:
            case str():  # これ以上入れ子がない
                return t.format(*tmpl_args)
            case list():
                targs = [self.apply(ta) for ta in tmpl_args]
                return t.format(*targs)
            case _:
                raise ValueError

    def expand(self, s: str) -> str:
        """文字列のテンプレを展開する."""
        txt = s
        called = CALL_MARKER.pick_nesting(s)
        if len(called) == 0:
            return txt
        for cl in called:
            sig = nested_tmpl_name_args(cl)
            fmt = self.apply(sig)
            if CALL_MARKER.contains(fmt):
                fmt = self.expand(fmt)
            old = CALL_MARKER.enclose(cl)
            txt = txt.replace(old, fmt)
        return txt
