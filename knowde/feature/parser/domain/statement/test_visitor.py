"""test statement visitor."""


from pytest_unordered import unordered

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.statement.visitor import tree2statements

"""

ctx
改行
統計情報
検索
用語との組み合わせ complex?
総数
"""


def test_multiline() -> None:
    """改行ありで一行とみなす."""
    _s = r"""
        # src
            aaa_\
            bbb
                ccc
            ddd
            mul1 \
                mul2 \
                    mul3
    """
    t = transparse(_s)
    s = tree2statements(t)
    assert s.strings == ["aaa_bbb", "ccc", "ddd", "mul1 mul2 mul3"]


def test_parse_context() -> None:
    """名前一覧."""
    _s = r"""
        # context
            ctx1
                -> b1
                    -> bb1
                    -> bb2
                -> b2
                <- c
                <-> d
                e.g. example
                g.e. general
                ref. ref
                1. one
                2. two
    """
    _t = transparse(_s)
    st = tree2statements(_t).contexted("ctx1")
    assert st.thus == unordered(["b1", "b2"])
    assert st.cause == unordered(["c"])
    assert st.example == unordered(["example"])
    assert st.general == unordered(["general"])
    assert st.ref == unordered(["ref"])
    assert st.list == ["one", "two"]
