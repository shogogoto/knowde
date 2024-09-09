"""textから章節を抜き出す."""

import pytest
from lark import Tree

from knowde.feature.parser.domain.knowde import KnowdeTree


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


@pytest.fixture()
def kt() -> KnowdeTree:
    """Fixture."""
    _s = r"""
        # source1

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
            ! var
            xxx
                xxx{name1}xxx
        #### 4.1
            ! context
            ctx1
            -> b1
            -> b2
            <- c
            <-> d
            e.g. example
            g.e. general
            ref. ref
        ##### 5.1
        ###### 6.1
        ### 3. dedent
        ### 3. same level
        ### 3. same level


        # source2
        ## 2. WS
            aaa
            bbb
        other tree line
            hhh
                iii
        !C2
    """
    return KnowdeTree.create(_s)


def test_parse_sources(kt: KnowdeTree) -> None:
    """見出しの階層."""
    # st = kt.get_source("source1")
    # st.info
    _echo(kt.tree)

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
