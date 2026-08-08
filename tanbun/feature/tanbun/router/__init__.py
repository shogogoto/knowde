"""router."""

from functools import cache

from fastapi import APIRouter, Depends

from tanbun.feature.tanbun.domain import TanbunChains, TanbunSearchResult
from tanbun.feature.tanbun.repo import search_tanbun
from tanbun.feature.tanbun.repo.cypher import WherePhrase
from tanbun.feature.tanbun.repo.detail import fetch_tanbun_chains
from tanbun.feature.user.router_util import TrackUser

from .params import SearchParam, get_search_param


@cache
def tanbun_router() -> APIRouter:
    """Router."""
    return APIRouter()


@tanbun_router().get("/")
async def search_by_text(
    param: SearchParam = Depends(get_search_param),
    user: TrackUser = None,
) -> TanbunSearchResult:
    """文字列検索."""
    t = WherePhrase[param.type]
    return await search_tanbun(param.q, t, param.paging, param.order)


@tanbun_router().get("/sentence/{sentence_id}")
async def detail(sentence_id: str, user: TrackUser = None) -> TanbunChains:
    """単文詳細."""
    return await fetch_tanbun_chains([sentence_id])
