"""parser utils."""
from lark import Token, Tree

from .const import LINE_TYPES
from .errors import LineMismatchError


def get_line(t: Tree) -> str:
    """Line treeから値を1つ返す."""
    # 直下がlineだった場合
    cl = t.children
    first = cl[0]
    if isinstance(first, Token) and first.type in LINE_TYPES:
        return str(first)
    if isinstance(first, Tree):
        if first.data == "ctx":
            return get_line(first.children[1])
        return get_line(first)
    raise LineMismatchError
