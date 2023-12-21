from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

if TYPE_CHECKING:
    from .domain import Reference

ref_router = APIRouter(
    prefix="/references",
    tags=["reference"],
)


@ref_router.get("")
def _get() -> list[Reference]:
    return []
