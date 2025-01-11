"""ネットワーク1 node1のview."""


from enum import Enum
from typing import Any, Callable, TypeAlias

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import SysArg
from knowde.complex.systats.nw1_n1 import (
    get_conclusion,
    get_details,
    get_premise,
    get_refer,
    get_referred,
)

SysContextFn: TypeAlias = Callable[[SysNet, SysArg], Any]


class SysContext(Enum):
    """文脈."""

    DETAIL = ("detail", get_details)
    REFER = ("ref", get_refer)
    REFERRED = ("rd", get_referred)
    PREMISE = ("pre", get_premise)
    CONCLUSION = ("con", get_conclusion)

    prefix: str
    fn: SysContextFn

    def __init__(self, prefix: str, fn: SysContextFn) -> None:
        """For merge."""
        self.prefix = prefix
        self.fn = fn
