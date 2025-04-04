"""data transfer object."""

from pydantic import BaseModel, Field


class PropositionParam(BaseModel, frozen=True):
    """interface用."""

    text: str = Field(title="文章")
