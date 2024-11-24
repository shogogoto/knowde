"""ナビ 任意sysnodeの位置を把握する羅針盤."""
from __future__ import annotations

from pydantic import BaseModel

from knowde.complex.system.domain.sysnet.sysnode import SysNode


class CurrentCoord(BaseModel, frozen=True):
    """現在位置."""

    node: SysNode
    heading_path: list[str]
    axiom_paths: list[list[SysNode]]
    leaf_paths: list[list[SysNode]]
    preds: list[SysNode]
    succs: list[SysNode]


class Navi(BaseModel, frozen=True):
    """現在位置を."""

    cunnret: CurrentCoord
