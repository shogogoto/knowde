"""parse treeを再帰的に解析."""
from __future__ import annotations

from typing import TypeAlias

from lark import Tree
from lark.visitors import Interpreter
from pydantic import Field

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg, SysNode
from knowde.primitive.__core__.nxutil import Direction, EdgeType

TReturn: TypeAlias = tuple[SysNode, EdgeType, Direction]


class SysNetInterpreter(Interpreter[SysNode, TReturn]):
    """SysNet構築."""

    sn: SysNet = Field(default_factory=lambda: SysNet(root="dummy"))

    def h1(self, tree: Tree) -> SysNet:  # noqa: D102
        first = tree.children[0]
        self.sn = SysNet(root=first)
        self._add_siblings(tree, first)
        self.sn.add_resolved_edges()
        self.sn.replace_quoterms()
        return self.sn

    def _add_siblings(self, tree: Tree, parent: SysNode) -> list[SysNode]:
        """兄弟を設定."""
        siblings = []
        self.sn.add_arg(parent)
        for c in tree.children[1:]:
            if isinstance(c, Tree):
                n, t, d = self.visit(c)
                self.sn.add_directed(t, d, parent, n)
                if t == EdgeType.BELOW:
                    siblings.append(n)
            else:
                siblings.append(c)
        self.sn.add(EdgeType.SIBLING, *siblings)
        return siblings

    def block(self, tree: Tree) -> TReturn:  # noqa: D102
        parent = tree.children[0]
        children = self._add_siblings(tree, parent)
        if len(children) > 0:
            self.sn.add_directed(EdgeType.BELOW, Direction.FORWARD, parent, children[0])
        return parent, EdgeType.BELOW, Direction.FORWARD

    def ctxline(self, tree: Tree) -> TReturn:  # noqa: D102
        t, d = tree.children[0]
        parent = tree.children[1]
        if isinstance(parent, Tree):
            n, t_, d_ = self.visit(parent)
            parent = n
        return parent, t, d

    def __default__(self, tree: Tree) -> TReturn:
        """heading要素."""
        h = tree.children[0]
        self._add_siblings(tree, h)
        return h, EdgeType.HEAD, Direction.FORWARD


def add_dipath(d: Direction, t: EdgeType, sn: SysNet, *ns: SysArg) -> None:
    """方向を追加."""
    match d:
        case Direction.FORWARD:
            sn.add(t, *ns)
        case Direction.BACKWARD:
            sn.add(t, *reversed(ns))
        case Direction.BOTH:
            sn.add(t, *reversed(ns))
            sn.add(t, *ns)
        case _:
            raise TypeError
