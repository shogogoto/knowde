"""nw1n1の周辺情報というか文脈詳細というか."""
from pydantic import BaseModel


class CtxDetail(BaseModel, frozen=True):
    """1nodeの詳細."""
