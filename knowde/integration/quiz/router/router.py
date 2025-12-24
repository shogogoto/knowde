"""quiz router."""

from fastapi import APIRouter

_r = APIRouter(prefix="/quiz", tags=["quiz"])


@_r.get("")
async def question_quiz():
    """問題を取得."""


@_r.post("")
async def answer_quiz():
    """回答を保存."""


def quiz_router() -> APIRouter:  # noqa: D103
    return _r
