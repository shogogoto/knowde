"""言明モデル."""
from pydantic import BaseModel


class Statement(BaseModel, frozen=True):
    """言明."""

    value: str
