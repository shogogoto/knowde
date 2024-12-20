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
        self._common(tree, first)
        self.sn.add_resolved_edges()
        return self.sn

    def _common(self, tree: Tree, parent: SysNode) -> list[SysNode]:
        ls = []
        # print("#" * 80, "common", parent)
        for c in tree.children:
            if isinstance(c, Tree):
                # print(parent, c)
                n, t, d = self.visit(c)
                add_dipath(d, t, self.sn, parent, n)
                if t == EdgeType.BELOW:
                    ls.append(n)
            else:
                ls.append(c)
        self.sn.add(EdgeType.SIBLING, *ls)
        return ls

    def block(self, tree: Tree) -> TReturn:  # noqa: D102
        p = tree.children[0]
        if isinstance(p, Tree):
            sub = Tree("block", tree.children[1:])
            c, t, d = self.visit(p)
            f2 = self._common(sub, c)
            self.sn.add(EdgeType.SIBLING, c, *f2)
            return c, t, d
        f = self._common(tree, p)[0]
        return f, EdgeType.BELOW, Direction.FORWARD

    def ctxline(self, tree: Tree) -> TReturn:  # noqa: D102
        t, d = tree.children[0]
        c = tree.children[1]
        if isinstance(c, Tree):
            p = c.children[0]
            sub = c.children[1]
            return self._common(sub, p)[0], t, d
        return c, t, d

    def __default__(self, tree: Tree) -> TReturn:
        """heading要素."""
        h = tree.children[0]
        return self._common(tree, h)[0], EdgeType.HEAD, Direction.FORWARD


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
