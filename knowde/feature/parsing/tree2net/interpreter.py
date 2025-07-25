"""parse treeを再帰的に解析."""

from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Final

from lark import Token, Tree
from lark.visitors import Interpreter

from knowde.feature.parsing.tree2net.directed_edge import (
    DirectedEdgeCollection,
)
from knowde.shared.nxutil.edge_type import Direction, EdgeType
from knowde.shared.util import parted

if TYPE_CHECKING:
    from lark.tree import Branch

    from knowde.feature.parsing.sysnet.sysnode import KNode


H_TYPES: Final = [f"H{i}" for i in range(2, 7)]


def include_heading(children: list[Hashable]) -> list:
    """headingのみを取得."""
    return [c for c in children if isinstance(c, Token) and c.type in H_TYPES]


def exclude_heading(children: list[Hashable]) -> list:
    """heading以外を取得."""
    return [c for c in children if not (isinstance(c, Token) and c.type in H_TYPES)]


class SysNetInterpreter(Interpreter):
    """SysNet構築."""

    def __init__(self) -> None:  # noqa: D107
        self.col: DirectedEdgeCollection = DirectedEdgeCollection()
        self.root: Token | str = "__dummy__"

    def h1(self, tree: Tree) -> None:  # noqa: D102
        p = tree.children[0]
        self.root = p
        children = self.visit_children(tree)
        self._add_indent(children[1:], p)
        for c in include_heading(children[1:]):
            self.col.append(EdgeType.HEAD, Direction.FORWARD, p, c)

    def _add_indent(self, children: list[Branch], parent: KNode) -> None:
        """インデントを登録."""
        ex_heading = exclude_heading(children)
        if len(ex_heading) > 0:
            self.col.append(EdgeType.SIBLING, Direction.FORWARD, *ex_heading)
        for c in ex_heading:
            self.col.append(EdgeType.BELOW, Direction.FORWARD, parent, c)
            break

    def block(self, tree: Tree) -> Branch:  # noqa: D102
        p = tree.children[0]
        children = self.visit_children(tree)
        ctxs, ns = parted(children[1:], lambda x: isinstance(x, tuple))
        for n, t, d in ctxs:
            self.col.append(t, d, p, n)
        self._add_indent(ns, p)
        return p

    def ctxline(self, tree: Tree) -> tuple[Branch, EdgeType, Direction]:  # noqa: D102
        t, d = tree.children[0]
        parent = tree.children[1]
        if isinstance(parent, Tree):
            parent = self.visit(parent)
        return parent, t, d

    @staticmethod
    def attach(tree: Tree) -> tuple[Branch, EdgeType, Direction]:  # noqa: D102
        cs = tree.children[0].children
        t, d = cs[0]
        p = cs[1]
        return p, t, d

    # return self.ctxline(tree)

    def __default__(self, tree: Tree) -> Branch:  # noqa: PLW3201
        """Heading要素."""
        children = self.visit_children(tree)
        p = children[0]
        self._add_indent(children[1:], p)
        for c in include_heading(children[1:]):
            self.col.append(EdgeType.HEAD, Direction.FORWARD, p, c)
        return p
