"""ネットワーク1 node1のview."""


from enum import Enum

from knowde.complex.systats.nw1_n1 import (
    Nw1N1Fn,
    get_conclusion,
    get_detail,
    get_premise,
    get_refer,
    get_referred,
)


class SysContext(Enum):
    """文脈."""

    DETAIL = ("detail", get_detail)
    REFER = ("ref", get_refer)
    REFERRED = ("refd", get_referred)
    PREMISE = ("pre", get_premise)
    CONCLUSION = ("con", get_conclusion)

    prefix: str
    fn: Nw1N1Fn

    def __init__(self, prefix: str, fn: Nw1N1Fn) -> None:
        """For merge."""
        self.prefix = prefix
        self.fn = fn
