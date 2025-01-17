"""nw1n1の周辺情報というか文脈詳細というか."""
from enum import Enum, StrEnum
from typing import Self

from pydantic import BaseModel

from knowde.complex.systats.nw1_n1 import (
    Nw1N1Fn,
    get_conclusion,
    get_detail,
    get_premise,
    get_refer,
    get_referred,
)


class Nw1N1Label(StrEnum):
    """文脈タイプ."""

    DETAIL = "detail"
    REFER = "refer"
    REFERRED = "referred"
    PREMISE = "premise"
    CONCLUSION = "conclusion"


class SysContext(Enum):
    """1nw1n文脈."""

    DETAIL = (Nw1N1Label.DETAIL, get_detail)
    REFER = (Nw1N1Label.REFER, get_refer)
    REFERRED = (Nw1N1Label.REFERRED, get_referred)
    PREMISE = (Nw1N1Label.PREMISE, get_premise)
    CONCLUSION = (Nw1N1Label.CONCLUSION, get_conclusion)

    label: Nw1N1Label
    fn: Nw1N1Fn

    def __init__(self, label: Nw1N1Label, fn: Nw1N1Fn) -> None:
        """For merge."""
        self.label = label
        self.fn = fn

    @classmethod
    def from_label(cls, label: Nw1N1Label) -> Self:
        """Create from item."""
        for e in cls:
            if e.label == label:
                return e
        raise ValueError(label)


class CtxDetail(BaseModel, frozen=True):
    """1nw 1nodeの詳細."""
