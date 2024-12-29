"""file I/O for networkx graph."""
import json
from functools import cache
from pathlib import Path
from typing import Final

import networkx as nx

from knowde.primitive.__core__.nxutil.edge_type import EdgeType

_DIR_PATH = Path.home() / ".knowde"


@cache
def dir_path() -> Path:
    """ファイル保管用ディレクトリ."""
    _DIR_PATH.mkdir(parents=True, exist_ok=True)
    return _DIR_PATH


T_EDGE_KEY: Final = "type"


class TEdgeJson(json.JSONEncoder):
    """EdgeType serialize用."""

    def default(self, o: object) -> object:  # noqa: D102
        if isinstance(o, EdgeType):
            return o.name
        return super().default(o)

    @classmethod
    def as_enum(cls, d: dict) -> dict:
        """For json load."""
        if T_EDGE_KEY in d:
            d[T_EDGE_KEY] = EdgeType[d[T_EDGE_KEY]]
        return d


def nxwrite(g: nx.DiGraph, write_to: Path) -> None:
    """Graph -> file."""
    js = nx.node_link_data(g, edges="edges")
    write_to.write_text(json.dumps(js, cls=TEdgeJson))


def nxread(read_from: Path) -> nx.DiGraph:
    """Str -> Graph."""
    js = json.loads(read_from.read_text(), object_hook=TEdgeJson.as_enum)
    return nx.node_link_graph(js, directed=True, multigraph=True, edges="edges")
