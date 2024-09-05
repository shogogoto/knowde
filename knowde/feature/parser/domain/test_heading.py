"""textから章節を抜き出す."""


import pytest

from .heading import load_heading


def test_parse_heading() -> None:
    """章の抽象木を抜き出す."""
    s = r"""
        ## H2.1
        ### H3.1
        ### H3.2
        ## H2.2
        ### H3.3
        ### H3.4
        ### H3.5
        ## H2.3
    """

    tree = load_heading(s)

    with pytest.raises(KeyError):  # 1つ以上ヒット
        tree.get("H")

    with pytest.raises(KeyError):  # ヒットしない
        tree.get("H4")
    assert tree.count == 8  # noqa: PLR2004
    assert tree.info("H2.1") == (2, 2)
    assert tree.info("H2.2") == (2, 3)
    assert tree.info("H2.3") == (2, 0)
    assert tree.info("H3.1") == (3, 0)
