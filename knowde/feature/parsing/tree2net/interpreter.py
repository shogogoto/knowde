"""parse treeを再帰的に解析."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lark import Token, Tree
from lark.visitors import Interpreter

from knowde.feature.parsing.primitive.heading import exclude_heading, include_heading
from knowde.feature.parsing.tree2net.directed_edge import (
    DirectedEdgeCollection,
)
from knowde.shared.nxutil.edge_type import Direction, EdgeType
from knowde.shared.util import parted

if TYPE_CHECKING:
    from lark.tree import Branch

    from knowde.feature.parsing.sysnet.sysnode import KNode


class SysNetInterpreter(Interpreter):
    """SysNet構築."""

    def __init__(self) -> None:  # noqa: D107
        self.col: DirectedEdgeCollection = DirectedEdgeCollection()
        self.root: Token | str = "__dummy__"

    def h1(self, tree: Tree) -> None:  # noqa: D102
        p = tree.children[0]
        self.root = p
        children = self.visit_children(tree)
        self._add_indent(exclude_heading(children[1:]), p)
        self._add_indent(include_heading(children[1:]), p)

    def _add_indent(self, children: list[Branch], parent: KNode) -> None:
        """インデントを登録."""
        if len(children) > 0:
            self.col.append(EdgeType.SIBLING, Direction.FORWARD, *children)
        for c in children:
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

    def __default__(self, tree: Tree) -> Branch:  # noqa: PLW3201
        """Heading要素."""
        children = self.visit_children(tree)
        p = children[0]
        self._add_indent(exclude_heading(children[1:]), p)
        self._add_indent(include_heading(children[1:]), p)
        return p
