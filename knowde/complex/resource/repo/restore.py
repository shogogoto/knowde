"""db から sysnetを復元."""


from functools import cache
from typing import TYPE_CHECKING

import neo4j
import networkx as nx
from neomodel import db

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import DUMMY_SENTENCE, Def, KNode
from knowde.complex.__core__.sysnet.sysnode.merged_def import MergedDef
from knowde.complex.__core__.tree2net.directed_edge import DirectedEdgeCollection
from knowde.primitive.__core__.nxutil.edge_type import Direction, EdgeType
from knowde.primitive.__core__.types import Duplicable
from knowde.primitive.term import Term, check_and_merge_term

from . import LResource

if TYPE_CHECKING:
    from neo4j.graph import Relationship


@cache
def to_sysnode(n: neo4j.graph.Node) -> KNode:
    """neo4jから変換."""
    lb_name = next(iter(n.labels))
    match lb_name:
        case "Sentence" | "Head":
            return n.get("val")
        case "Term":
            return Term.create(n.get("val"))
        case "Resource":
            return n.get("title")
        case _:
            props = n.items()
            raise ValueError(props, lb_name)


def restore_sysnet(title: str) -> SysNet:
    """DBからSysNetを復元."""
    rsrc = LResource.nodes.get(title=title)
    q = """
        MATCH (root:Resource {uid: $uid})
        OPTIONAL MATCH (root)-[r1:HEAD|BELOW]->(top:Head|Sentence)
        RETURN r1 as r, root as s, top as e

        // 見出し
        UNION
        OPTIONAL MATCH (top)-[:HEAD]->*(hs:Head)-[rh:HEAD]->(he:Head)
        RETURN rh as r, hs as s, he as e

        // いろいろ
        UNION
        OPTIONAL MATCH (top)-[:BELOW|SIBLING]->*(n1:Sentence)
            <-[r2:BELOW|SIBLING|RESOLVED|DEF]-(n2:Sentence|Term|Head)
        return r2 as r, n2 as s, n1 as e

        // 複数名の用語がある場合
        UNION
        MATCH (n2)<-[r3:TERM]-(m:Term)
        RETURN r3 as r, m as s, n2 as e
    """
    res = db.cypher_query(q, params={"uid": rsrc.uid})
    col = DirectedEdgeCollection()
    defs = []
    for _rel, _, _ in res[0]:
        r: Relationship = _rel
        s = to_sysnode(_rel.start_node)
        e = to_sysnode(_rel.end_node)
        match r.type:
            case "TERM" if isinstance(s, Term) and isinstance(e, Term):
                term = Term(names=s.names + e.names)
                defs.append(Def.dummy(term))
            case "DEF" if isinstance(s, Term) and isinstance(e, (str, Duplicable)):
                s2 = Term.create(*s.names, alias=r.get("alias", None))
                d = Def.dummy(s2) if e == DUMMY_SENTENCE else Def(term=s2, sentence=e)
                defs.append(d)
            case "RESOLVED" | "SIBLING" | "BELOW" | "HEAD":
                t = EdgeType.__members__.get(r.type)
                col.append(t, Direction.FORWARD, s, e)
            case _:
                raise ValueError(r.type)
    g = nx.MultiDiGraph()
    col.add_edges(g)
    terms = [d.term for d in defs]
    mt = check_and_merge_term(terms)
    mdefs, stddefs = MergedDef.create_and_parted(mt, defs)
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]
    return SysNet(root=title, g=g)
