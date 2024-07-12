from operator import itemgetter
from uuid import UUID

import networkx as nx

from knowde._feature._shared.domain.container import Composite
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.location.domain import CompositionTree, Location
from knowde._feature.location.repo.label import REL_L2L_NAME, LocUtil, RelL2L


def add_location_root(name: str) -> Location:
    return LocUtil.new(name=name).to_model()


def add_sub_location(uid: UUID, name: str) -> Location:
    parent = LocUtil.find_by_id(uid=uid)
    sub = LocUtil.fetch(name=name)
    RelL2L.connect(parent.label, sub.label)
    return sub.to_model()


def remove_location(uid: UUID) -> None:
    LocUtil.delete(uid=uid)


def find_location_tree(uid: UUID) -> Composite[Location]:
    n = REL_L2L_NAME
    res = query_cypher(
        f"""
        MATCH (root:Location {{uid: $uid}})
        OPTIONAL MATCH (root)-[rel:{n}]->+(loc:Location)
        RETURN
            root,
            rel
        """,
        params={"uid": uid.hex},
    )
    root = res.get("root", convert=Location.to_model)[0]
    g = nx.DiGraph()
    for _rel in res.get("rel", row_convert=itemgetter(0)):
        rel = _rel[0]
        s = Location.to_model(rel.start_node())
        e = Location.to_model(rel.end_node())
        g.add_edge(s, e)
    return CompositionTree(root=root, g=g).build()
