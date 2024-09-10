"""textから章節を抜き出す."""

from datetime import date

import pytest
from lark import Tree

from knowde.feature.parser.domain.knowde import KnowdeTree
from knowde.feature.parser.domain.parser import transparse
from knowde.feature.parser.domain.source import THeading, TSource
from knowde.feature.parser.domain.statement import TStatemet


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


@pytest.fixture()
def kt() -> KnowdeTree:
    """Fixture."""
    _s = r"""
        # source1

            @author tanaka tarou
            @published 2020-11-11
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
            name4 = name5 = name6: def3
            name7:\
                deffffffffffffffffffffffffffffffffffffffffffffff
            alias |namenamename: defdefdefdef
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

    trans = THeading() * TSource() * TStatemet()
    t = transparse(_s, trans)
    return KnowdeTree(tree=t)


"""
知りたいこと
sourceごと
名前一覧
名前衝突チェック
言明一覧
言明の依存関係情報


文字列化

"""


def test_parse_sources(kt: KnowdeTree) -> None:
    """見出しの階層."""
    _echo(kt.tree)
    s1 = kt.get_source("source1")
    assert s1.title == "source1"
    assert s1.author == "tanaka tarou"
    assert s1.published == date(2020, 11, 11)
