"""test.

n_arg 1 2 3
name <, >  含む
"""
from __future__ import annotations

import pytest

from . import Template, Templates, get_template_signature
from .errors import (
    InvalidTemplateNameError,
    TemplateArgMismatchError,
    TemplateConflictError,
    TemplateNotFoundError,
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
        ("f<x>", ["f", ["x"]]),
        (" g<x, y>", ["g", ["x", "y"]]),
        # ("g<x,f<1, 2>, y>", ["g", ["x", ["f", ["1", "2"]], "y"]]),
        # ("g<f<1>, y>>>", ["g", [["f", ["1"]], "y"]]),
        # ("h<g<f<1>, y>, 2>", ["h", [["g", [["f", ["1"]], "y"]], 2]]),
    ],
)
def test_nested_template_signature(line: str, expected: list) -> None:
    """文字列からテンプレの名前と引数の値を再帰的に返す."""
    # print("#" * 30)
    assert get_template_signature(line) == expected


@pytest.mark.skip()
def test_1nested_template() -> None:
    """出力に埋め込んだテンプレを呼び出す."""
    t1 = Template.parse(r"f<x>: \\math{x}")
    t2 = Template.parse("g<x>: ~`f<x>`~")
    t3 = Template.parse("h<x, y>: y`g<f<x>>`y")
    t4 = Template.parse("not found<x>: xxx")
    assert not t1.is_nested
    assert t2.is_nested
    ts = Templates().add(t1, t2, t3)
    with pytest.raises(TemplateNotFoundError):
        ts.format(t4)
    # assert ts.format(t2, "X") == r"~\math{X}~"
    # print("#" * 30)

    assert ts.format(t3, "1", "!") == r"!~\\math{1}~!"
