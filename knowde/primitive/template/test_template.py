"""test.

n_arg 1 2 3
name <, >  含む
"""

from __future__ import annotations

import pytest

from . import Template, Templates, nested_tmpl_name_args
from .errors import (
    InvalidTemplateNameError,
    TemplateArgMismatchError,
    TemplateConflictError,
    TemplateNotFoundError,
    TemplateUnusedArgError,
)


@pytest.mark.parametrize(
    ("line"),
    [
        "A: aaa",
        "B, B1: bbb",
        "C: c{A}c",
        r"D: c{A}c \\ multi",
        "<=> f<x>: x",
        "<=> f<x>    :x",
        "f<x>:",
    ],
)
def test_template_disparsable(line: str) -> None:
    """テンプレ文字列ではない."""
    assert not Template.is_parsable(line)


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
    assert Template.is_parsable(line)
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


@pytest.mark.parametrize(("line"), [("f<x>:y"), ("f<x, y>:a")])
def test_unused_template_arg(line: str) -> None:
    """formatに使われる文字列が引数にない場合にエラー."""
    with pytest.raises(TemplateUnusedArgError):
        Template.parse(line)


def test_duplicate_templates() -> None:
    """テンプレが重複したときにエラー."""
    with pytest.raises(TemplateConflictError):
        Templates().add(
            Template.parse("f<x>: x"),
            Template.parse("f<y>: y"),
        )


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("f<>", ["f", []]),
        ("f <x>", ["f", ["x"]]),
        (" g<x, y>", ["g", ["x", "y"]]),
        ("g<x,f<1, 2>>", ["g", ["x", ["f", ["1", "2"]]]]),
        ("g<f<1>, y>>>", ["g", [["f", ["1"]], "y"]]),
        ("h<g<f<1>, y>, 2>", ["h", [["g", [["f", ["1"]], "y"]], "2"]]),
    ],
)
def test_nested_template_signature(line: str, expected: list) -> None:
    """文字列からテンプレの名前と引数の値を再帰的に返す."""
    assert nested_tmpl_name_args(line) == expected


def test_call_unadded_template() -> None:
    """未登録のテンプレを使用."""
    t1 = Template.parse("mul<x,y>: x * y")
    t2 = Template.parse("add<x,y>: x + y")
    ts = Templates().add(t1, t2)
    with pytest.raises(TemplateNotFoundError):
        ts.expand("_undef<1>_")


@pytest.mark.parametrize(
    ("line", "tgt", "expected"),
    [
        ("f <x>: xx", "af<1>a", "a11a"),
        ("f <x>: !x!", "f<1>f<2>", "!1!!2!"),
    ],
)
def test_template_nesting_call(line: str, tgt: str, expected: str) -> None:
    """テンプレートのformに含まれるテンプレート呼び出し."""
    t = Template.parse(line)
    assert t.apply(tgt, *t.embedded_args(tgt)) == expected


def test_1nested_template() -> None:
    """出力に埋め込んだテンプレを呼び出す."""
    t1 = Template.parse(r"f<x, y>: math{x, y}")
    t2 = Template.parse("g<x>: ~_f<x, x>_~")
    t3 = Template.parse("h<x, y>: y_g<f<x, y>>_y")
    ts = Templates().add(t1, t2, t3)
    assert ts.expand("_g<X>_") == r"~math{X, X}~"
    assert ts.expand("_h<1,2>_") == r"2~math{math{1, 2}, math{1, 2}}~2"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("nocall", "nocall"),
        ("_i<A>_", "AA~#!A!#~AA"),
    ],
)
def test_expand_templates(line: str, expected: str) -> None:
    """文字列に含まれたテンプレを展開."""
    ts = Templates().add(
        Template.parse("f<x>: !x!"),
        Template.parse("g<x>: #x#"),
        Template.parse("h<x>: ~_g<f<x>>_~"),
        Template.parse("i<x>: xx_h<x>_xx"),
    )
    assert ts.expand(line) == expected
