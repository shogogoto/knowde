from __future__ import annotations

from pydantic import BaseModel


class TermResolver(BaseModel):
    """temp."""

    atomics: dict[str, str]
