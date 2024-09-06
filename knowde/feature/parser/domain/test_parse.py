"""textから章節を抜き出す."""


from textwrap import dedent

from knowde.feature.parser.domain.comment import TComment
from knowde.feature.parser.domain.heading import HeadingVisitor, THeading
from knowde.feature.parser.domain.parser import common_parser, transparse


def _align(s: str) -> str:
    return dedent(s).strip()


def test_parse_whitespace() -> None:
    """空をパースしてエラーにならない."""
    p = common_parser(debug=True).parse
    p("")
    p(
        """
""",
    )
    p(
        """
    """,
    )
    common_parser().parse(
        """

        """,
    )


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
    _t = transparse(s, THeading())
    v = HeadingVisitor()
    # print(_t)
    # print(_t.pretty())
    v.visit(_t)
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


def test_parse_with_comment() -> None:
    """コメント付き章の抽象木を抜き出す."""
    s = r"""
    ## H2
    ! c1
    ! c2
    ### H3
    ! c3
    ! c4 with #
    ! c5
    ## H4
    """
    _tree = transparse(s, TComment() * THeading())
    # print(_tree)
    # print(_tree.pretty())
    # v = CommentVisitor()
    # v.visit(_tree)
    # cd = v.d
    # assert cd.strs("H2") == ["c1", "c2"]
    # assert cd.strs("H3") == ["c3", "c4", "c5"]
    # assert cd.strs("H4") == []


def test_parse_statement() -> None:
    """コメント付き章の抽象木を抜き出す."""
    _s = r"""
    ! c1
    stmt1
    stmt2 \
        stmt3
    stmt4_indent
        child1
        child2
            grandchild
    """
    _t = transparse(_s, TComment() * THeading())
    # print(t)
    # print(t.pretty())
    # load_statement(s)
