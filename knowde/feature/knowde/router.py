"""router."""

from functools import cache
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from knowde.feature.knowde import KAdjacency, KnowdeDetail
from knowde.feature.knowde.cypher import OrderBy, Paging, WherePhrase
from knowde.feature.knowde.detail import detail_knowde
from knowde.feature.knowde.repo import search_knowde


@cache
def knowde_router() -> APIRouter:
    """Router."""
    return APIRouter(prefix="/knowde", tags=["knowde"])


class SearchParam(BaseModel):
    """検索パラメータ."""

    q: str = Query("")
    type: str = Query(WherePhrase.CONTAINS.name, enum=[p.name for p in WherePhrase])
    paging: Paging = Field(default_factory=Paging)
    order: OrderBy | None = None


def get_search_param(  # noqa: PLR0917
    q: str = Query(""),
    type: str = Query(WherePhrase.CONTAINS.name, enum=[p.name for p in WherePhrase]),  # noqa: A002
    page: int = Query(default=1, gt=0),
    size: int = Query(default=100, gt=0),
    n_detail: int = Query(default=1),
    n_premise: int = Query(default=3),
    n_conclusion: int = Query(default=3),
    n_refer: int = Query(default=3),
    n_referred: int = Query(default=3),
    dist_axiom: int = Query(default=1),
    dist_leaf: int = Query(default=1),
    desc: bool = Query(default=True),  # noqa: FBT001
) -> SearchParam:
    """orderByがうまく変換されなかったので噛ませた."""
    paging = Paging(page=page, size=size)
    order = OrderBy(
        n_detail=n_detail,
        n_premise=n_premise,
        n_conclusion=n_conclusion,
        n_refer=n_refer,
        n_referred=n_referred,
        dist_axiom=dist_axiom,
        dist_leaf=dist_leaf,
        desc=desc,
    )
    return SearchParam(q=q, type=type, paging=paging, order=order)


class KnowdeSearchResult(BaseModel):
    """knowde検索結果."""

    total: int
    data: list[KAdjacency]


@knowde_router().get("/")
def search_by_text(
    param: SearchParam = Depends(get_search_param),
) -> KnowdeSearchResult:
    """文字列検索."""
    t = WherePhrase[param.type]
    tot, data = search_knowde(param.q, t, param.paging, param.order)
    return KnowdeSearchResult(total=tot, data=data)


@knowde_router().get("/sentence/{sentence_id}")
def detail(sentence_id: UUID) -> KnowdeDetail:
    """knowde詳細."""
    return detail_knowde(sentence_id)
