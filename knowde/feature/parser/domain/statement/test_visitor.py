"""test statement visitor."""

from pytest_unordered import unordered

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.statement.statement import Statement

"""

ctx
改行
統計情報
検索
用語との組み合わせ complex?
総数
"""


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
    # _rt = get_source(_t, "context")
    # _echo(_t)
    # st = _rt.statement("ctx1")
    st = Statement.create("ctx1", _t)
    assert st.thus == unordered(["b1", "b2"])
    assert st.cause == unordered(["c"])
    assert st.example == unordered(["example"])
    assert st.general == unordered(["general"])
    assert st.ref == unordered(["ref"])
    assert st.list == ["one", "two"]
