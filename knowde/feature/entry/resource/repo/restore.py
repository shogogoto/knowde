"""db から sysnetを復元."""

from functools import cache
from math import isinf
from uuid import UUID

import neo4j
import networkx as nx
from neomodel.async_.core import AsyncDatabase

from knowde.feature.knowde.repo.cypher import q_call_sent_names
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.primitive.time import WhenNode
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import (
    DUMMY_SENTENCE,
    DummySentence,
    KNode,
    add_def_edge,
)
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import UUIDy, to_uuid


@cache
def to_sysnode(n: neo4j.graph.Node) -> tuple[KNode, str]:
    """neo4jから変換."""
    lb_name = next(iter(n.labels))
    match lb_name:
        case "Sentence" | "Head":
            retval = n.get("val")
            if retval == DUMMY_SENTENCE:
                retval = DummySentence(uid=n.get("uid"))
        case "Term":
            retval = Term.create(n.get("val"))
        case "Resource" | "Entry":
            retval = n.get("title")
        case "Interval":
            d = dict(n)
            d["n"] = d.pop("val")
            for k in ("start", "end"):  # infはJSONに変換できない
                if isinf(d[k]):
                    d[k] = None
            retval = WhenNode.model_validate(d)
        case _:
            props = n.items()
            raise ValueError(props, lb_name)
    return retval, lb_name


async def restore_tops(resource_uid: UUIDy) -> tuple[nx.DiGraph, dict[UUID, KNode]]:
    """SysNetを先のHeadまたはSentenceまで復元."""
    q = """
        MATCH (root:Resource {uid: $uid})
        MATCH (root)-[:HEAD]->*(s:Head)-[r:HEAD|BELOW]->(e:Head|Sentence)
        RETURN r, s, e
        UNION
        MATCH (root:Resource {uid: $uid})
        MATCH (root)-[r:HEAD|BELOW]->(e:Head|Sentence)
        RETURN r, root as s, e
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"uid": to_uuid(resource_uid).hex},
    )
    g = nx.MultiDiGraph()
    uids = {}
    for row in rows:
        r, s_, e_ = row
        suid = to_uuid(s_.get("uid"))
        euid = to_uuid(e_.get("uid"))
        uids[suid], _ = to_sysnode(s_)
        uids[euid], _ = to_sysnode(e_)
        EdgeType(r.type.lower()).add_edge(g, suid, euid)
    return g, uids


async def restore_undersentnet(  # noqa: PLR0914
    resource_uid: UUIDy,
) -> tuple[nx.DiGraph, dict[UUID, KNode], dict[UUID, Term]]:
    """top以下のsentenceやdefのネットワークを復元."""
    various = "|".join([
        et.name for et in EdgeType if et not in {EdgeType.HEAD, EdgeType.DEF}
    ])
    q = f"""
        MATCH (s:Sentence {{resource_uid: $uid}})
        OPTIONAL MATCH (s)-[r:{various}]->(e:Sentence|Interval)
        {q_call_sent_names("s")}
        RETURN s
            , COLLECT([e, r]) as ends
            , COALESCE(names, []) as names
            , alias
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"uid": to_uuid(resource_uid).hex},
    )
    g = nx.MultiDiGraph()
    uids: dict[UUID, KNode] = {}
    terms: dict[UUID, Term] = {}
    for row in rows:
        s, ends, names, alias = row
        names = [n.get("val") for n in names]
        sval, _ = to_sysnode(s)
        suid = to_uuid(s.get("uid"))
        uids[suid] = sval
        g.add_node(suid)
        for end in ends:
            e, r = end
            if e is None:
                continue
            euid = to_uuid(e.get("uid"))
            EdgeType(r.type.lower()).add_edge(g, suid, euid)
            uids[euid], _ = to_sysnode(e)
        if len(names) > 0:
            term = Term.create(*names, alias=alias)
            terms[suid] = term
    return g, uids, terms


async def restore_graph(resource_uid: UUIDy) -> tuple[nx.DiGraph, dict[UUID, KNode]]:
    """SysNetのgraphを復元."""
    g1, uids1 = await restore_tops(resource_uid)
    g2, uids2, terms2 = await restore_undersentnet(resource_uid)
    for uid, term in terms2.items():
        add_def_edge(g2, uids2[uid], term)
    g = nx.compose(g1, g2)
    uids = {**uids1, **uids2}
    return g, uids


async def restore_sysnet(resource_uid: UUIDy) -> tuple[SysNet, dict[KNode, UUID]]:
    """SysNetを復元."""
    g, uids = await restore_graph(resource_uid)
    g_relabeled = nx.relabel_nodes(g, uids)
    uid_reverse = {v: k for k, v in uids.items()}
    return SysNet(g=g_relabeled, root=uids[to_uuid(resource_uid)]), uid_reverse
