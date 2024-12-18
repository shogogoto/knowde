"""parse tree to sysnet."""
from __future__ import annotations

from typing import TypeAlias

from lark import Tree
from lark.visitors import Interpreter
from pydantic import BaseModel, Field

from knowde.complex.system.sysnet import SysNet
from knowde.complex.system.sysnet.sysnode import SysArg, SysNode
from knowde.core.nxutil import Direction, EdgeType
from knowde.feature.parser.tree2net.transformer import TSysArg
from knowde.primitive.parser import parse2tree
from knowde.primitive.parser.testing import treeprint


def parse2net(txt: str) -> SysNet:
    """文からsysnetへ."""
    _t = parse2tree(txt, TSysArg())
    treeprint(_t)
    return SysNetInterpreter().visit(_t)


H_DATA = [f"h{i}" for i in range(2, 7)]

TReturn: TypeAlias = tuple[SysNode, EdgeType, Direction]


# 子ブロックの先頭がCTXのとき
class SysNetInterpreter(Interpreter[SysNode, TReturn], BaseModel):
    """SysNet構築."""

    sn: SysNet = Field(default_factory=lambda: SysNet(root="dummy"))

    def _common(self, tree: Tree) -> list[SysNode]:
        parent = tree.children[0]
        self.sn.add_nodes(parent)
        ls = [parent]
        for c in tree.children[1:]:
            if isinstance(c, Tree):
                n, t, d = self.visit(c)
                self.sn.add_nodes(n)
                add_dipath(d, t, self.sn, parent, n)
                if t == EdgeType.BELOW:
                    ls.append(n)
            else:
                ls.append(c)
        self.sn.add(EdgeType.SIBLING, *ls)
        return ls

    def h1(self, tree: Tree) -> SysNet:  # noqa: D102
        first = tree.children[0]
        self.sn = SysNet(root=first)
        self._common(tree)
        self.sn.add_resolved_edges()
        return self.sn

    def block(self, tree: Tree) -> TReturn:  # noqa: D102
        return self._common(tree)[0], EdgeType.BELOW, Direction.FORWARD

    def ctxline(self, tree: Tree) -> TReturn:  # noqa: D102
        c1 = tree.children[0]
        c2 = tree.children[1]
        t, d = c1
        if isinstance(c2, Tree):
            self.sn.g.add_node(c2)
            n, t, d = self.visit(c1)
            self.sn.g.add_node(n)
            add_dipath(d, t, self.sn, c2, n)
        return c2, t, d

    def __default__(self, tree: Tree) -> TReturn:
        """heading要素."""
        return self._common(tree)[0], EdgeType.HEAD, Direction.FORWARD


def add_dipath(
    d: Direction,
    t: EdgeType,
    sn: SysNet,
    *ns: SysArg,
) -> list[SysArg]:
    """方向を追加."""
    match d:
        case Direction.FORWARD:
            return sn.add(t, *ns)
        case Direction.BACKWARD:
            return sn.add(t, *reversed(ns))
        case Direction.BOTH:
            sn.add(t, *reversed(ns))
            return sn.add(t, *ns)


# return datetime.strptime(v, "%Y-%m-%d").astimezone(TZ).date()
