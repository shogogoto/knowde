"""parse errors."""
from textwrap import dedent


class ParserError(Exception):
    """独自定義."""


class UndedentError(ParserError):
    """不正インデント検出."""


class UnexpectedPivotError(ParserError):
    """不正インデント検出のあり得ないpivot値."""


class KnSyntaxError(ParserError):
    """自作構文エラー."""

    def __str__(self) -> str:
        """エラー文."""
        ctx, line, _ = self.args
        return f"{self.label} at line {line}.\n{ctx}"


class HeadingMismatchError(KnSyntaxError):
    """見出しレベル."""

    label = "Heading Level Mismatch"


class MissingTopHeadingError(KnSyntaxError):
    """見出しH1が存在しない."""

    label = "Missing Top Heading(H1)"


class MissingIndentError(KnSyntaxError):
    """見出し下の行にインデントがない."""

    label = "Missing Indent"


class AttachDetailError(KnSyntaxError):
    """付加情報(attach)の配下に文は置けない."""

    label = "Invalid sentence placed under attach context"


_head_lv = [
    """
    # h1
    ### h2
""",
    """
    # h1
    ## h2
    #### h4
""",
    """
    # h1
    ## h2
    ### h3
    ##### h5
""",
    """
    # h1
    ## h2
    ### h3
    #### h4
    ###### h6
""",
]

_top = """
    aaaa
"""
_indent = [
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
    """
    # 1
    !aaa
""",
    """
    # 1
    ## 2
    !aaa
""",
    """
    # 1
    ## 2
    ### 3
    !aaa
""",
    """
    # 1
    ## 2
    ### 3
    #### 4
    !aaa
""",
    """
    # 1
    ## 2
    ### 3
    #### 4
    ##### 5
    !aaa
""",
    """
    # 1
    ## 2
    ### 3
    #### 4
    ##### 5
    ###### 6
    !aaa
""",
]

_attach = [
    """
    # 1
      aaa
        when. 100
          bbb
    """,
    """
    # 1
    ## 2
      aaa
        when. 100
          bbb
    """,
    """
    # 1
    ## 2
    ### 3
      aaa
        when. 100
          bbb
    """,
    """
        # 1
        ## 2
        ### 3
        #### 4
          aaa
            when. 100
              bbb
            """,
    """
        # 1
        ## 2
        ### 3
        #### 4
        ##### 5
          aaa
            when. 100
              bbb
            """,
    """
        # 1
        ## 2
        ### 3
        #### 4
        ##### 5
        ###### 6
          aaa
            when. 100
              bbb
            """,
]


# for match examples
HEAD_ERR_EXS = {
    HeadingMismatchError: list(map(dedent, _head_lv)),
    MissingTopHeadingError: [dedent(_top)],
    MissingIndentError: list(map(dedent, _indent)),
    AttachDetailError: list(map(dedent, _attach)),
}


# def handle_error(e: UnexpectedToken) -> bool:
#     """エラー処理."""
#     # if e.token.type == "$END":
#     #     return True
#     print("#" * 80)
#     # print(e.expected, e.token.type)
#     # print(type(e))
#     print(e.considered_rules)
#     print(e.token.type, e.token, e.token_history)
#     print("#" * 80)
#     return False
