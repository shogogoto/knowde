"""用語関連."""


import pytest
from pytest_unordered import unordered

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.term.domain import Term, TermConflictError
from knowde.feature.parser.domain.term.visitor import get_termspace

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
    """用語の衝突の検知."""
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
          n1,n11:
          P1 |line,l1:
          P2 |def,d1: def
        ## h2
          n2,n21:
          P3 |line2,l2,l21:
          P4 |def2,d2: def
          P5 |aaa
    """
    t = transparse(_s)
    s = get_termspace(t)
    assert s.origins == unordered(
        [
            Term.create("n1", "n11"),
            Term.create("line", "l1", alias="P1"),
            Term.create("def", "d1", alias="P2"),
            Term.create("n2", "n21"),
            Term.create("line2", "l2", "l21", alias="P3"),
            Term.create("def2", "d2", alias="P4"),
            Term.create(alias="P5"),
        ],
    )


# def test_formula() -> None:
#     """数式に含まれる=は無視して文字列として扱いたい."""
#     _s = r"""
#         # h1
#           量化子の順序によって意味が変わる
#             n1: $\forall{x}\exists{y}R(x, y=t)$
#             n2=n22: xx$R(x, y=t)$xx
#         ## h2
#           P1 |xx$y=t$xx
#           P2 |xx$y=t$xx \
#                   xxxx
#             <-> J13 |サールの反証: {平叙文}から{評価文}を結論する論証
#             e.g. P41|「XXXならば明日ヒョウが降るよw」
#     """
#     t = transparse(_s)
#     x = get_termspace(t)
#     assert len(x) == 3
#     assert x.aliases == unordered(["P1", "P2", "J13", "P41"])
