"""用語関連."""


import pytest

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.term.domain import TermConflictError
from knowde.feature.parser.domain.term.visitor import get_termspace
from knowde.feature.parser.domain.testing import echo_tree

"""
用語グループ一覧
用語グループ数
見出しごとの用語数

用語の関連を調べる
    用語の説明に含まれる用語
    用語を利用した言明の検索

用語の参照
"""


def test_conflict_name() -> None:
    """用語の衝突の検知.

    どことどこの名前が衝突したか
        headingの特定.
    """
    _s = r"""
        # names
            name1:
            name1:
    """
    t = transparse(_s)
    with pytest.raises(TermConflictError):
        get_termspace(t)


def test_parse_terms() -> None:
    """用語一覧."""
    _s = r"""
        # h1
          n1=n11:
          P1 |line=l1:
          P2 |def=d1: def
        ## h2
          n2=n21:
          P3 |line2=l2=l21:
          P4 |def2=d2: def
          P5 |aaa
    """
    t = transparse(_s)
    x = get_termspace(t)
    assert len(x) == 6  # noqa: PLR2004
    assert len(x.aliases) == 5  # noqa: PLR2004


def test_formula() -> None:
    """数式に含まれる=は無視して文字列として扱いたい."""
    _s = r"""
        # h1
          量化子の順序によって意味が変わる
            n1: $\forall{x}\exists{y}R(x, y=t)$
            n2=n22: xx$R(x, y=t)$xx
        ## h2
          P1 |xx$y=t$xx
          P2 |xx$y=t$xx \
                  xxxx
    """
    t = transparse(_s)
    x = get_termspace(t)
    echo_tree(t)
    assert len(x) == 2  # noqa: PLR2004
    assert len(x.aliases) == 2  # noqa: PLR2004
