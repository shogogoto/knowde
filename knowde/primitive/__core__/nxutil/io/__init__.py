"""file I/O for networkx graph."""
import json
from pathlib import Path

import networkx as nx

from knowde.primitive.__core__.nxutil.edge_type import TEdgeJson


def nxwrite(g: nx.DiGraph, write_to: Path) -> None:
    """Graph -> file."""
    js = nx.node_link_data(g)
    write_to.write_text(json.dumps(js, cls=TEdgeJson), encoding="utf8")


def nxread(read_from: Path) -> nx.DiGraph:
    """Str -> Graph."""
    js = json.loads(read_from.read_text(), object_hook=TEdgeJson.as_enum)
    return nx.node_link_graph(js, directed=True, multigraph=True)
