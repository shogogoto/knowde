"""repository."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from knowde.primitive.proposition.domain import Proposition

from .label import PropositionUtil


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


def complete_proposition(pref_uid: str) -> Proposition:
    """補完."""
    return PropositionUtil.complete(pref_uid=pref_uid).to_model()
