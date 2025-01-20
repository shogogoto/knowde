"""test.

n_arg 1 2 3
name <, >  含む
"""
from __future__ import annotations

import pytest

from . import Template
from .errors import (
    InvalidTemplateNameError,
    TemplateArgMismatchError,
    TemplateUnusedArgError,
)


@pytest.mark.parametrize(
    ("line", "args", "output", "name"),
    [
        # n_arg 1
        ("f<x>: abcxyz", ["a"], "abcayz", "f"),
        (" g < x >: (x, x)", ["abc"], "(abc, abc)", "g"),
        # n_arg 2
        ("func<x,  y >: x ~ y", ["X", "Y"], "X ~ Y", "func"),
        # n_arg 3
        ("f<x, y, z>: x + y + z", ["1", "2", "3"], "1 + 2 + 3", "f"),
    ],
)
def test_template(line: str, args: list[str], output: str, name: str) -> None:
    """普通のテンプレ."""
    tmpl = Template.parse(line)
    assert tmpl.format(*args) == output
    assert tmpl.name == name


# 引数文字を含まないformにする意図はないはずだからエラー?
#  いや、繰り返しの文字列を共通化するためには、引数なしの定数templateが欲しくなるかも
@pytest.mark.parametrize(
    ("line", "args"),
    [
        ("f<x>:x", []),
        ("f<x>:x", ["a", "b"]),
        ("f<x,y,z>:xyz", ["a", "b"]),
    ],
)
def test_template_args_mismatch(line: str, args: list[str]) -> None:
    """引数が合わない."""
    with pytest.raises(TemplateArgMismatchError):
        Template.parse(line).format(*args)


@pytest.mark.parametrize(
    ("line"),
    [
        (">f<x>:x"),
        ("<f<x>:x"),
        ("><f<x>:x"),
        ("<>f<x>:x"),
    ],
)
def test_invalid_template_name(line: str) -> None:
    """名前がmark文字列を含む."""
    with pytest.raises(InvalidTemplateNameError):
        Template.parse(line)


@pytest.mark.parametrize(
    ("line"),
    [
        ("f<x>:y"),
        ("f<x, y>:a"),
    ],
)
def test_unused_template_arg(line: str) -> None:
    """formatに使われる文字列が引数にない場合にエラー."""
    with pytest.raises(TemplateUnusedArgError):
        Template.parse(line)


# 入力にテンプレを含む場合は考えない <- f<x>: _g<_h<x>_>_
#  みたいにテンプレートを定義すればいい
def test_template_with_output() -> None:
    """出力にテンプレを含む."""
