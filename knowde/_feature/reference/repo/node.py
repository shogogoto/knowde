from textwrap import dedent
from uuid import UUID

import networkx as nx
from neomodel import NeomodelPath, db

from knowde._feature.reference.domain import Reference
from knowde._feature.reference.domain.domain import ReferenceGraph

from .label import ref_util


def add_reference(name: str) -> Reference:
    return ref_util.create(name=name).to_model()


def add_part(parent_id: UUID, name: str) -> Reference:
    parent = ref_util.find_one(parent_id)
    part = ref_util.create(name=name)
    part.label.parent.connect(parent.label)
    return part.to_model()


def find_reference(uid: UUID) -> ReferenceGraph:
    q = dedent(
        """
    MATCH (tgt:Reference) WHERE tgt.uid=$uid
    MATCH p = (tgt)<-[rel:INCLUDED*]-(child:Reference)
    RETURN p
    """,
    ).strip()
    results, meta = db.cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )
    g = nx.DiGraph()
    for row in results:
        x: NeomodelPath = row[0]
        models = ref_util.to_labels(x.nodes).to_model()
        nx.add_path(g, models)
    return ReferenceGraph(G=g, uid=uid)
