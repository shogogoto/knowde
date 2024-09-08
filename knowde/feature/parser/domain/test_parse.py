"""textから章節を抜き出す."""

from lark import Tree

from knowde.feature.parser.domain.comment import TComment
from knowde.feature.parser.domain.indent import IndentRule
from knowde.feature.parser.domain.parser import (
    transparse,
)


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


def test_parse_heading() -> None:
    """見出しの階層."""
    _s = r"""
        # 1.1
            author: tanaka tarou
            published: 2020-11-11

            aaa_\
            bbb
                ccc
                ddd
        ## 2.1
        ### 3.1
        #### 4.1
        ##### 5.1
        ###### 6.1
            ppp
            !aaaaa
            ! csdcsdacsad
        ### 3. down
        ### 3. indent heading
            qqq
            rrr
        ### 3. indent heading2
        # 1. 2th
        ## 2. WS
        ggg
            hhh
                iii
        !C2
    """

    _t = transparse(_s, TComment())
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
