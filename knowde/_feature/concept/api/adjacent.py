from __future__ import annotations

from fastapi import APIRouter

from knowde._feature.concept.api.util import PREFIX, TAG
from knowde._feature.concept.domain.rel import ConnectedConcept  # noqa: TCH001
from knowde._feature.concept.repo.repo import complete_concept
from knowde._feature.concept.repo.repo_rel import find_adjacent

concept_adj_router = APIRouter(
    prefix=f"{PREFIX}/adjacent",
    tags=[f"{TAG}/adjacent"],
)


@concept_adj_router.get("")
def _get(pref_uid: str) -> list[ConnectedConcept]:
    """Search concept by startswith uid."""
    c = complete_concept(pref_uid)
    return find_adjacent(c.valid_uid).flatten()
