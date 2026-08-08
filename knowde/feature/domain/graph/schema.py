"""知識グラフのAPI schema."""

from typing import Annotated, Any

import networkx as nx
from pydantic import BaseModel, PlainSerializer, PlainValidator, ValidationInfo

from .edge_type import EdgeType


def _validate_graph(v: Any, info: ValidationInfo) -> nx.DiGraph:
    if isinstance(v, dict):
        return nx.node_link_graph(v, edges="edges")
    if isinstance(v, nx.DiGraph):
        return v
    raise TypeError


class _EdgeData(BaseModel):
    """FastAPI schema用の辺."""

    type: EdgeType
    source: str
    target: str
    key: int


class _GraphData(BaseModel):
    """FastAPI schema用のグラフ."""

    directed: bool
    edges: list[_EdgeData]
    graph: dict
    multigraph: bool
    nodes: list[dict[str, str]]


NXGraph = Annotated[
    nx.DiGraph,
    PlainValidator(_validate_graph, json_schema_input_type=dict),
    PlainSerializer(
        lambda x: nx.node_link_data(x, edges="edges"),
        return_type=_GraphData,
    ),
]
