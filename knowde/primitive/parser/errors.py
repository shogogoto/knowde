"""parse errors."""
from textwrap import dedent


class KnSyntaxError(SyntaxError):
    """自作構文エラー."""

    def __str__(self) -> str:
        """エラー文."""
        ctx, line, _ = self.args
        # print(self)
        return f"{self.label} at line {line}.\n{ctx}"


class HeadingMismatchError(KnSyntaxError):
    """見出しレベル."""

    label = "Heading Level Mismatch"


exs = [
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
# for match examples
HEAD_ERR_EXS = {
    HeadingMismatchError: list(map(dedent, exs)),
}
