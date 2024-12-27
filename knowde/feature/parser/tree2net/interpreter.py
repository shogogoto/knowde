"""parse treeを再帰的に解析."""
from __future__ import annotations

from itertools import filterfalse
from typing import TYPE_CHECKING, Callable, Final, Hashable, TypeAlias

from lark import Token, Tree
from lark.visitors import Interpreter
from pydantic import Field

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysNode
from knowde.primitive.__core__.nxutil import Direction, EdgeType

if TYPE_CHECKING:
    from lark.tree import Branch

TReturn: TypeAlias = tuple[SysNode]


H_TYPES: Final = [f"H{i}" for i in range(2, 7)]


def partition(it: iter, f: Callable[..., bool]) -> tuple[list, list]:
    """iterを条件で2分割."""
    return list(filter(f, it)), list(filterfalse(f, it))


def include_heading(children: list[Hashable]) -> list:
    """headingのみを取得."""
    return [c for c in children if isinstance(c, Token) and c.type in H_TYPES]


def exclude_heading(children: list[Hashable]) -> list:
    """heading以外を取得."""
    return [c for c in children if not (isinstance(c, Token) and c.type in H_TYPES)]


class SysNetInterpreter(Interpreter[SysNode, TReturn]):
    """SysNet構築."""

    sn: SysNet = Field(default_factory=lambda: SysNet(root="dummy"))  # 差し替えられる

    def h1(self, tree: Tree) -> SysNet:  # noqa: D102
        p = tree.children[0]
        self.sn = SysNet(root=p)
        children = self.visit_children(tree)
        self._add_indent(children[1:], p)
        for c in include_heading(children[1:]):
            self.sn.add_directed(EdgeType.HEAD, Direction.FORWARD, p, c)
        self.sn.add_resolved_edges()
        self.sn.replace_quoterms()
        return self.sn

    def _add_indent(self, children: list[Branch], parent: SysNode) -> None:
        """インデントを登録."""
        ex_heading = exclude_heading(children)
        self.sn.add_directed(EdgeType.SIBLING, Direction.FORWARD, *ex_heading)
        for c in ex_heading:
            self.sn.add_directed(EdgeType.BELOW, Direction.FORWARD, parent, c)
            break

    def block(self, tree: Tree) -> TReturn:  # noqa: D102
        p = tree.children[0]
        children = self.visit_children(tree)
        ctxs, ns = partition(children[1:], lambda x: isinstance(x, tuple))
        for n, t, d in ctxs:
            self.sn.add_directed(t, d, p, n)
        self._add_indent(ns, p)
        return p

    def ctxline(self, tree: Tree) -> TReturn:  # noqa: D102
        t, d = tree.children[0]
        parent = tree.children[1]
        if isinstance(parent, Tree):
            parent = self.visit(parent)
        return parent, t, d

    def __default__(self, tree: Tree) -> TReturn:
        """Heading要素."""
        children = self.visit_children(tree)
        p = children[0]
        self._add_indent(children[1:], p)
        for c in include_heading(children[1:]):
            self.sn.add_directed(EdgeType.HEAD, Direction.FORWARD, p, c)
        return p
