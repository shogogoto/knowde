"""test parsing."""

from textwrap import dedent

import pytest

from knowde.primitive.parser import parse2tree
from knowde.primitive.parser.errors import (
    HeadingMismatchError,
    MissingIndentError,
    MissingTopHeadingError,
)


@pytest.mark.parametrize(
    ("txt"),
    map(
        dedent,
        [
            """
        # 1
        #### 4
        """,
            """
        # 1
        ## 2
        ##### 5
        """,
            """
        # 1
        ## 2
        ### 3
        ###### 6
        """,
            """
        # 1
        ## 2
        ### 3
        #### 4
        ###### 6
        """,
        ],
    ),
)
def test_parse_heading_level_error(txt: str) -> None:
    """見出しの階層ずれ."""
    with pytest.raises(HeadingMismatchError):
        parse2tree(txt)


def test_parse_missing_top_heading() -> None:
    """H1なし."""
    _s = """
        aaaa
    """
    with pytest.raises(MissingTopHeadingError):
        parse2tree(_s)


@pytest.mark.parametrize(
    ("txt"),
    map(
        dedent,
        [
            """
        # 1
        aaa
        """,
            """
        # 1
        ## 2
        aaa
        """,
            """
        # 1
        ## 2
        ### 3
        aaa
        """,
            """
        # 1
        ## 2
        ### 3
        #### 4
        aaa
        """,
            """
        # 1
        ## 2
        ### 3
        #### 4
        ##### 5
        aaa
        """,
            """
        # 1
        ## 2
        ### 3
        #### 4
        ##### 5
        ###### 6
        aaa
        """,
        ],
    ),
)
def test_parse_missing_indent(txt: str) -> None:
    """インデントなしエラー."""
    with pytest.raises(MissingIndentError):
        parse2tree(txt)
