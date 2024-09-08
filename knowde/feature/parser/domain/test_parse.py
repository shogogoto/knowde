"""textから章節を抜き出す."""

from lark import Tree

from knowde.feature.parser.domain.comment import TComment
from knowde.feature.parser.domain.parser import (
    transparse,
)


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


"""

"""


def test_parse_heading() -> None:
    """見出しの階層."""
    _s = r"""
        # 1.1

            author tanaka tarou
            published 2020-11-11
            xxx
        ## 2.1
            ! multiline
            aaa_\
            bbb
                ccc
                ddd
                mul1 \
                    mul2 \
                        mul3
        ### 3.1
            ! define
            name1: def1
            name2=name3: def2
        #### 4.1
        ##### 5.1
        ###### 6.1
        ### 3. dedent
        ### 3. same level
        ### 3. same level
        # 1 other tree
        ## 2. WS
        other tree line
            hhh
                iii
        !C2
    """

    _t = transparse(_s, TComment())
    _echo(_t)

    # _r = IndentRule()
    # _r.visit(_t)
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
