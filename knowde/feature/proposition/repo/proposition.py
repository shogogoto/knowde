"""命題repo."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde.feature.proposition.repo.label import PropositionUtil

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.feature.proposition.domain import Proposition


def add_proposition(text: str) -> Proposition:
    """命題の追加."""
    return PropositionUtil.create(text=text).to_model()


def change_proposition(uid: UUID, text: str) -> Proposition:
    """命題の文章の変更."""
    return PropositionUtil.change(uid=uid, text=text).to_model()


def delete_proposition(uid: UUID) -> None:
    """命題の削除."""
    PropositionUtil.delete(uid)


def list_propositions() -> list[Proposition]:
    """命題一覧."""
    return PropositionUtil.find().to_model()
