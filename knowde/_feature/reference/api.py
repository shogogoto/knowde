from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from knowde._feature.reference.repo.node import add_part, add_root, find_roots

from .domain import Reference  # noqa: TCH001

if TYPE_CHECKING:
    from uuid import UUID

ref_router = APIRouter(
    prefix="/references",
    tags=["reference"],
)


@ref_router.get("")
def _get() -> list[Reference]:
    return find_roots().roots


@ref_router.post("")
def add_ref(name: str) -> Reference:
    return add_root(name)


@ref_router.post("/{ref_id}")
def add_subref(ref_id: UUID, name: str) -> Reference:
    return add_part(ref_id, name)
