"""DTO for proposition."""
from __future__ import annotations

from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model


class PropositionParam(BaseModel, frozen=True):
    """for 命題."""

    text: str


PartialPropositionParam = create_partial_model(PropositionParam)
