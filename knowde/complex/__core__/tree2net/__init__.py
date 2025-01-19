"""parse tree to sysnet."""
from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysfn import (
    check_duplicated_sentence,
    to_def,
    to_term,
)
from knowde.complex.__core__.sysnet.sysfn.build_fn import (
    add_resolved_edges,
    replace_quoterms,
)
from knowde.complex.__core__.sysnet.sysnode.merged_def import MergedDef
from knowde.complex.__core__.tree2net.directed_edge import DirectedEdgeCollection
from knowde.primitive.parser import get_leaves, parse2tree
from knowde.primitive.parser.testing import treeprint
from knowde.primitive.term import check_and_merge_term
from knowde.primitive.term.markresolver import MarkResolver

from .interpreter import SysNetInterpreter
from .transformer import TSysArg

if TYPE_CHECKING:
    from lark import Tree


def parse2net(txt: str, do_print: bool = False) -> SysNet:  # noqa: FBT001 FBT002
    """文からsysnetへ."""
    _t = parse2tree(txt, TSysArg())
    if do_print:
        treeprint(_t, True)  # noqa: FBT003
    si = SysNetInterpreter()
    si.visit(_t)
    g = _build_graph(_t, si.col)
    return SysNet(root=si.root, g=g)


def _build_graph(tree: Tree, col: DirectedEdgeCollection) -> nx.MultiDiGraph:
    g, resolver = _extract_leaves(tree)
    col.add_edges(g)
    add_resolved_edges(g, resolver)
    replace_quoterms(g, resolver)
    return nx.freeze(g)


def _extract_leaves(tree: Tree) -> tuple[nx.MultiDiGraph, MarkResolver]:
    """transformedなASTを処理."""
    leaves = get_leaves(tree)
    mt = check_and_merge_term(to_term(leaves))
    check_duplicated_sentence(leaves)
    mdefs, stddefs = MergedDef.create_and_parted(mt, to_def(leaves))
    g = nx.MultiDiGraph()
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]
    return g, MarkResolver.create(mt)
