"""textから章節を抜き出す."""

from lark import Tree

from knowde.feature.parser.domain.comment import TComment
from knowde.feature.parser.domain.heading import THeading
from knowde.feature.parser.domain.indent import IndentRule
from knowde.feature.parser.domain.parser import (
    transparse,
)


def test_example_indenter() -> None:
    """公式の例.

    https://lark-parser.readthedocs.io/en/latest/examples/indented_tree.html#sphx-glr-examples-indented-tree-py.
    """
    _tree_grammar = r"""
        ?start: _NL* tree
        tree: NAME _NL [_INDENT tree+ _DEDENT]
        %import common.CNAME -> NAME
        %import common.WS_INLINE
        %declare _INDENT _DEDENT
        %ignore WS_INLINE
        _NL: /(\r?\n[\t ]*)+/
    """
    _s = """
    a
        b
        c
            d
            e
        f
            g
    """
    _p = transparse
    _t = _p(_s, TComment())
    _echo(_t)

    r = IndentRule()
    r.visit(_t)


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


def test_parse_whitespace() -> None:
    """空をパースしてエラーになる様子を確認."""
    _p = transparse
    _x = """
"""
    _x2 = """
    """
    _x3 = """

"""
    _x4 = """

    """
    _ = _p("")
    _ = _p(_x)
    _ = _p(_x2)
    _ = _p(_x3)
    _ = _p(_x4)


def test_parse_heading() -> None:
    """見出しの階層."""
    _s = r"""
        # 1.1
        aaa
        bbb
            ccc
            ddd
        ## 2.1
        ### 3.1
        #### 4.1
        ##### 5.1
        ###### 6.1
        ### 3. down
        ### 3. indent heading
        ### 3. indent heading2
            eee
                fff
        # 1. 2th
        ## 2. WS
        ggg
            hhh
                iii
    """

    _t = transparse(_s, THeading())
    _echo(_t)

    _r = IndentRule()
    _r.visit(_t)
    # v = HeadingVisitor()
    # v.visit(_t)
    # tree = v.tree
    # with pytest.raises(KeyError):  # 1つ以上ヒット
    #     tree.get("H")
    # with pytest.raises(KeyError):  # ヒットしない
    #     tree.get("H4")
    # assert tree.count == 8
    # assert tree.info("H2.1") == (2, 2)
    # assert tree.info("H2.2") == (2, 3)
    # assert tree.info("H2.3") == (2, 0)
    # assert tree.info("H3.1") == (3, 0)


def test_parse_comment() -> None:
    """コメント付き."""
    _s = r"""
    ! toplevel
    ## H2
    ! c1
    ! c2
    ### H3
    ! c3
    ! c4 with #
    ! c5
    ! c6
    ## H4
    """
    # _t = transparse(_s, debug=True)
    # _echo(_t)


#     # # v = CommentVisitor()
#     # v.visit(_t)
#     # cd = v.d
#     # assert cd.strs("H2") == ["c1", "c2"]
#     # assert cd.strs("H3") == ["c3", "c4", "c5"]
#     # assert cd.strs("H4") == []

# multiline \
#     continue
# multiline2_\
#     continue2_\
#         continue3


def test_parse_statement() -> None:
    """記述."""
    _s = r"""
    ! c1
    stmt1
    stmt4_indent
        child1
        child2
            grandchild
        child3
            gc2
        child4

    """
    # aaa: yyy
    # _t = transparse(_s, debug=True)  # , THeading() * TComment())
    # print(_t)
    # print(_t.pretty())
