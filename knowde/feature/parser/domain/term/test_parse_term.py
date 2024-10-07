"""用語関連."""


import pytest
from pytest_unordered import unordered

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


# 用語空間の合併レベルを指定するか
#  どういうレイアウトで用語一覧を見たいか
#  バリエーションはあるべきか
def test_parse_names() -> None:
    """用語一覧.

    nameのみ
    line
    define
    """
    _s = r"""
        # h1
          n1=n11:
          P1 |line=l1:
          P2 |def=d1: def
        ## h2
          n2=n21:
          P3 |line2=l2:

          P4 |def2=d2: def
          P5 |aaa
    """
    t = transparse(_s)
    echo_tree(t)
    x = get_termspace(t)
    assert x.aliases == unordered([f"P{i}" for i in range(1, 6)])


# def test_find_names() -> None:
#     """検索."""
