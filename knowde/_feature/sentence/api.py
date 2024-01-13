from fastapi import APIRouter

from knowde._feature._shared.api import set_basic_router

from .repo.label import s_util

s_router = set_basic_router(
    s_util,
    APIRouter(prefix="/sentence", tags=["sentence"]),
)
