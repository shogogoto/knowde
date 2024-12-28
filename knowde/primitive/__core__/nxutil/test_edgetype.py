"""test."""
import json

from .edge_type import EdgeType, TEdgeJson


def test_encode_t_edge() -> None:
    """Enum encode."""
    d = {"type": EdgeType.TO}

    txt = json.dumps(d, cls=TEdgeJson)
    assert d == json.loads(txt, object_hook=TEdgeJson.as_enum)
