"""parse tree to sysnet."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.tree2net.directed_edge import (
    add_resolved_edges,
    replace_quoterms,
)
from knowde.complex.__core__.tree2net.directed_edge.extraction import extract_leaves
from knowde.primitive.parser import parse2tree
from knowde.primitive.parser.testing import treeprint

from .interpreter import SysNetInterpreter
from .transformer import TSysArg

if TYPE_CHECKING:
    import networkx as nx


def parse2net(txt: str, do_print: bool = False) -> SysNet:  # noqa: FBT001 FBT002
    """文からsysnetへ."""
    _t = parse2tree(txt, TSysArg())
    if do_print:
        treeprint(_t, True)  # noqa: FBT003
    si = SysNetInterpreter()
    si.visit(_t)
    g, resolver = extract_leaves(_t)
    si.col.add_edges(g)
    add_resolved_edges(g, resolver)
    replace_quoterms(g, resolver)
    return SysNet(root=si.root, g=g)
    # return si.sn


def parse2graph(txt: str, do_print: bool = False) -> nx.MultiDiGraph:  # noqa: FBT001 FBT002
    """文からsysnetへ(remake)."""
    _t = parse2tree(txt, TSysArg())
    if do_print:
        treeprint(_t, True)  # noqa: FBT003
    si = SysNetInterpreter()
    si.visit(_t)

    g, resolver = extract_leaves(_t)
    si.col.add_edges(g)
    add_resolved_edges(g, resolver)
    replace_quoterms(g, resolver)
    return g
