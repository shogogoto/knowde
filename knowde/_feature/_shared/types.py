from __future__ import annotations

from typing import Annotated, Any

import networkx as nx
from networkx import DiGraph
from pydantic import (
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
)

from knowde._feature._shared.repo.base import LBase


def _validate_neomodel(
    v: Any,  # noqa: ANN401
    info: ValidationInfo,  # noqa: ARG001
) -> LBase:
    if isinstance(v, LBase):
        return v
    raise TypeError


NeoModel = Annotated[
    LBase,
    PlainValidator(_validate_neomodel),
    PlainSerializer(lambda x: x.__properties__),
]


def _validate_graph(v: Any, info: ValidationInfo) -> DiGraph:  # noqa: ARG001 ANN401
    if isinstance(v, DiGraph):
        return v
    raise TypeError


NXGraph = Annotated[
    DiGraph,
    PlainValidator(_validate_graph),
    PlainSerializer(lambda x: nx.node_link_data(x)),
]
