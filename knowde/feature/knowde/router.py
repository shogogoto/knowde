"""router."""

from functools import cache

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from knowde.feature.knowde import KAdjacency
from knowde.feature.knowde.cypher import OrderBy, Paging, WherePhrase
from knowde.feature.knowde.repo import search_knowde


@cache
def knowde_router() -> APIRouter:
    """Router."""
    return APIRouter(prefix="/knowde", tags=["knowde"])


class SearchParam(BaseModel):
    """検索パラメータ."""

    q: str = ".*"
    type: str = Query(WherePhrase.REGEX.name, enum=[p.name for p in WherePhrase])
    paging: Paging = Field(default_factory=Paging)
    order: OrderBy | None = None


@knowde_router().get("/")
def search_by_text(
    param: SearchParam = Query(default=SearchParam()),
) -> list[KAdjacency]:
    """文字列検索."""
    t = WherePhrase[param.type]
    return search_knowde(param.q, t, param.paging, param.order)
