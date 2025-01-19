"""test."""


from knowde.primitive.template import Template


def test_template() -> None:
    """普通のテンプレ."""
    txt = "f<x>: abcxyz"

    tmpl = Template.parse(txt)
    assert tmpl("a") == "abcayz"


def test_2level_template() -> None:
    """二階テンプレ."""
