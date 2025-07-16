"""router."""

from functools import cache
from uuid import UUID

from fastapi import APIRouter, Depends

from knowde.feature.knowde import KnowdeDetail
from knowde.feature.knowde.repo import search_knowde
from knowde.feature.knowde.repo.cypher import WherePhrase
from knowde.feature.knowde.repo.detail import chains_knowde
from knowde.shared.user.router_util import TrackUser

from .params import (
    KnowdeSearchResult,
    SearchParam,
    get_search_param,
)


@cache
def knowde_router() -> APIRouter:
    """Router."""
    return APIRouter(prefix="/knowde", tags=["knowde"])


@knowde_router().get("/")
def search_by_text(
    param: SearchParam = Depends(get_search_param),
    user: TrackUser = None,
) -> KnowdeSearchResult:
    """文字列検索."""
    t = WherePhrase[param.type]
    tot, data = search_knowde(param.q, t, param.paging, param.order)
    return KnowdeSearchResult(total=tot, data=data)


@knowde_router().get("/sentence/{sentence_id}")
def detail(sentence_id: UUID, user: TrackUser = None) -> KnowdeDetail:
    """knowde詳細."""
    return chains_knowde(sentence_id)
