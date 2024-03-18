"""application service."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import db

from knowde._feature.term.repo.label import TermUtil
from knowde.feature.definition.dto import DetailView
from knowde.feature.definition.repo.deep_search import find_recursively

if TYPE_CHECKING:
    from uuid import UUID


def detail_service(term_uid: UUID) -> DetailView:
    """定義の詳細."""
    with db.transaction:
        if not TermUtil.find_one_or_none(uid=term_uid):
            return DetailView(detail=None)
        return DetailView(
            detail=find_recursively(term_uid).build(),
        )
