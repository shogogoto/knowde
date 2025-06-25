"""file I/O for networkx graph."""

import json
from pathlib import Path
from typing import Final
from uuid import UUID

import networkx as nx
from pydantic import BaseModel

from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.sysnet.sysnode import (
    DUMMY_SENTENCE,
    DummySentence,
)
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import Duplicable

T_EDGE_KEY: Final = "type"


class NxJsonalyzer(json.JSONEncoder):
    """nxgraph to serialize用."""

    def default(self, o: object) -> object:  # noqa: D102
        if isinstance(o, EdgeType):
            return o.name
        if isinstance(o, BaseModel):
            return o.model_dump()
        if isinstance(o, frozenset):
            return list(o)
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)

    @classmethod
    def restore(cls, d: object) -> object:
        """For json load."""
        if T_EDGE_KEY in d:
            d[T_EDGE_KEY] = EdgeType[d[T_EDGE_KEY]]
        if "names" in d:
            d = Term.model_validate(d)
        if "uid" in d:
            if d["n"] == DUMMY_SENTENCE:
                d = DummySentence.model_validate(d)
            else:
                d = Duplicable.model_validate(d)
        return d


def nx2json_dump(g: nx.DiGraph, indent: int = 2) -> str:
    """Graph to json dump."""
    js = nx.node_link_data(g, edges="edges")
    return json.dumps(js, cls=NxJsonalyzer, indent=indent, ensure_ascii=False)


def nxwrite(g: nx.DiGraph, write_to: Path) -> None:
    """Graph -> file."""
    write_to.write_text(nx2json_dump(g))


def nxread(txt: str) -> nx.DiGraph:
    """Str -> Graph."""
    js = json.loads(
        txt,
        object_hook=NxJsonalyzer.restore,
    )
    return nx.node_link_graph(js, directed=True, multigraph=True, edges="edges")
