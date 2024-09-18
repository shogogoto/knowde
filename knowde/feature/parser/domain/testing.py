"""test helper."""
from lark import Tree


def echo(t: Tree) -> None:
    """Print tree."""
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201
