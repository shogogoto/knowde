from __future__ import annotations

from pydantic import BaseModel


class BookParam(BaseModel):
    title: str


class SectionParam(BaseModel):
    values: list[str]
