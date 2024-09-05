"""textから章節を抜き出す."""


import pytest

from knowde.feature.parser.domain.comment import load_with_comment

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


def test_parse_heading_with_comment() -> None:
    """コメント付き章の抽象木を抜き出す."""
    s = r"""
        ## H2
        ! c1
        ! c2
        ### H3
        ! c3
        ! c4
        ! c5
        ## H4
    """

    cd = load_with_comment(s)
    assert cd.strs("H2") == ["c1", "c2"]
    assert cd.strs("H3") == ["c3", "c4", "c5"]
    assert cd.strs("H4") == []


def test_parse_statement() -> None:
    """コメント付き章の抽象木を抜き出す."""
    _s = r"""
        ## H2
        ! c1
        stmt1
        stmt2 \
            stmt3
    """
    # load_statement(s)
