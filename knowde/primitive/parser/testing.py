"""test helper."""
from lark import Tree


def treeprint(t: Tree, echo: bool = False) -> None:  # noqa: FBT001 FBT002
    """Print tree."""
    print(t.pretty())  # noqa: T201
    if echo:
        print(t)  # noqa: T201
