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
from knowde.primitive.term.errors import MarkUncontainedError


def parse2net(txt: str, do_print: bool = False) -> SysNet:  # noqa: FBT001 FBT002
    """文からsysnetへ."""
    _t = parse2tree(txt, TSysArg())
    if do_print:
        treeprint(_t, True)  # noqa: FBT003
    si = SysNetInterpreter()
    try:
        si.visit(_t)
    except MarkUncontainedError as e:
        print(e)  # noqa: T201
    return si.sn


TReturn: TypeAlias = tuple[SysNode, EdgeType, Direction]


class SysNetInterpreter(Interpreter[SysNode, TReturn], BaseModel):
    """SysNet構築."""

    sn: SysNet = Field(default_factory=lambda: SysNet(root="dummy"))

    def h1(self, tree: Tree) -> SysNet:  # noqa: D102
        first = tree.children[0]
        self.sn = SysNet(root=first)
        # print("#" * 80, "h1")
        self._add_siblings(tree, first)
        # print("#" * 80, "h1 end")
        # self.sn.add_resolved_edges()
        return self.sn

    def _add_siblings(self, tree: Tree, parent: SysNode) -> list[SysNode]:
        """兄弟を設定."""
        siblings = []
        # print("#" * 80, "sib", parent)
        for c in tree.children[1:]:
            if isinstance(c, Tree):
                n, t, d = self.visit(c)
                add_dipath(d, t, self.sn, parent, n)
                if t == EdgeType.BELOW:
                    siblings.append(n)
            else:
                siblings.append(c)
        # print("#" * 80, "sib end", parent, siblings)
        self.sn.add(EdgeType.SIBLING, parent, *siblings)
        return siblings

    def block(self, tree: Tree) -> TReturn:  # noqa: D102
        parent = tree.children[0]
        # print("block::", parent, len(tree.children[1:]))
        children = self._add_siblings(tree, parent)
        if len(children) > 0:
            add_dipath(Direction.FORWARD, EdgeType.BELOW, self.sn, parent, children[0])
        # print("block::end", children)
        return parent, EdgeType.BELOW, Direction.FORWARD

    def ctxline(self, tree: Tree) -> TReturn:  # noqa: D102
        # print("ctxline::", tree)
        t, d = tree.children[0]
        parent = tree.children[1]
        if isinstance(parent, Tree):
            return self.visit(parent)
        return parent, t, d

    def __default__(self, tree: Tree) -> TReturn:
        """heading要素."""
        h = tree.children[0]
        self._add_siblings(tree, h)
        return h, EdgeType.HEAD, Direction.FORWARD


def add_dipath(
    d: Direction,
    t: EdgeType,
    sn: SysNet,
    *ns: SysArg,
) -> list[SysArg]:
    """方向を追加."""
    # print("*****add_dipath::", t, ns)
    match d:
        case Direction.FORWARD:
            return sn.add(t, *ns)
        case Direction.BACKWARD:
            return sn.add(t, *reversed(ns))
        case Direction.BOTH:
            sn.add(t, *reversed(ns))
            return sn.add(t, *ns)


# return datetime.strptime(v, "%Y-%m-%d").astimezone(TZ).date()
