from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.reference.domain.domain import Reference, ReferenceGraph

from .label import ref_util

if TYPE_CHECKING:
    from uuid import UUID

    from neomodel import NeomodelPath


def add_rootref(name: str) -> Reference:
    return ref_util.create(name=name).to_model()


def delete_ref(ref_id: UUID) -> None:
    """配下のrefも全て削除."""
    return ref_util.delete(ref_id)


# def rename_ref(ref_id: UUID, name: str) -> Reference:
#     lb = ref_util.find_one(ref_id).label
#     lb.name = name
#     return Reference.to_model()


def find_roots(ref_id: UUID) -> ReferenceGraph:
    results, meta = query_cypher(
        """
        MATCH (tgt:Reference) WHERE tgt.uid=$uid
        OPTIONAL MATCH p = (tgt)<-[rel:INCLUDED*]-(child:Reference)
        RETURN p
        """,
        params={"uid": ref_id.hex},
        resolve_objects=True,
    )
    g = nx.DiGraph()
    for row in results:
        if row[0] is None:
            continue
        x: NeomodelPath = row[0]
        models = ref_util.to_labels(x.nodes).to_model()
        nx.add_path(g, models)
    return ReferenceGraph(G=g, uid=ref_id)


# def add_subref(parent_id: UUID) -> None:
#     pass


# def change_ref(name: str) -> None:
#     pass


def squeeze() -> None:
    """削除して、childrenを親の子とする."""


# def move_refs(
#     parent_id: UUID | None = None,
# ) -> None:
#     """childrenを自身の兄弟にする."""
