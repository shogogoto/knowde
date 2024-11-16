"""用語解決."""
from __future__ import annotations

from pydantic import BaseModel


class TermResolver(BaseModel):
    """用語解決器."""

    atomics: dict[str, str]


# def resolve_term(term: str, d: dict) -> None:
#     pass
