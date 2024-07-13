"""application service."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from knowde.feature.definition.dto import DetailView
from knowde.feature.definition.repo.deep_search import find_recursively
from knowde.feature.definition.repo.definition import RelDefUtil


def detail_service(def_uid: UUID) -> DetailView:
    """定義の詳細."""
    if not RelDefUtil.find_one_or_none(def_uid):
        return DetailView(detail=None)
    return DetailView(
        detail=find_recursively(def_uid).build(),
    )
