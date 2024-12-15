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


def test_parse_missing_indent() -> None:
    """H1なし."""
    _s = """
        # h1
        aaaa
    """
    with pytest.raises(MissingIndentError):
        parse2tree(_s)


# def test_json_parser() -> None:
#     try:
#         json_parse('{"example1": "value"')
#     except JsonMissingClosing as e:
#         print(e)

#     try:
#         json_parse('{"example2": ] ')
#     except JsonMissingOpening as e:
#         print(e)


_s2 = r"""
    # 1
        @author tanaka tarou
        @published 2020-11-11
        xxx
    ## 2
        ! multiline
    ### 3
        ! define
        xxx
    #### 4
    ##### 5
    ###### 6
    ### 31
    ### 32
    ### 33
    # source2
    other tree line
        hhh
    !C2
"""
