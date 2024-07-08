from pydantic import BaseModel, Field


class PropositionParam(BaseModel, frozen=True):
    text: str = Field(title="文章")
