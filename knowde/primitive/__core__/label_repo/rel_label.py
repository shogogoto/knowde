"""neomodel関係の基礎."""
from neomodel import IntegerProperty

from knowde.primitive.__core__.label_repo.base import RelBase


class RelOrder(RelBase):
    """順番を持つ関係."""

    order = IntegerProperty()
