"""test helper."""
from lark import Tree


def treeprint(t: Tree) -> None:
    """Print tree."""
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201
