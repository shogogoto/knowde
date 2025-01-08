"""非pydanticデータ型を対応させる."""
from __future__ import annotations

from typing import Annotated, Any

import networkx as nx
from neomodel import StructuredNode
from pydantic import (
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
)


def _validate_neomodel(
    v: Any,  # noqa: ANN401
    info: ValidationInfo,  # noqa: ARG001
) -> StructuredNode:
    if isinstance(v, StructuredNode):
        return v
    raise TypeError


NeoModel = Annotated[
    StructuredNode,
    PlainValidator(_validate_neomodel),
    PlainSerializer(lambda x: x.__properties__),
]


def _validate_graph(v: Any, info: ValidationInfo) -> nx.DiGraph:  # noqa: ARG001 ANN401
    if isinstance(v, nx.DiGraph):
        return v
    raise TypeError


NXGraph = Annotated[
    nx.MultiDiGraph,
    PlainValidator(_validate_graph),
    PlainSerializer(lambda x: nx.node_link_data(x)),
]
