"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature.concept.error import NotUniqueFoundError
from knowde._feature.concept.repo.repo_rel import connect

from .label import LConcept, to_model

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.concept.domain import Concept
    from knowde._feature.concept.domain.domain import SaveProp


def save_concept(c: SaveProp) -> Concept:
    """Create concept."""
    lc = LConcept(**c.model_dump()).save()
    saved = to_model(lc)
    for sid in c.src_ids:
        connect(sid, saved.valid_uid)
    for did in c.dest_ids:
        connect(saved.valid_uid, did)
    return saved
    # return find_adjacent(saved.valid_uid)


def list_concepts() -> list[Concept]:
    """Find all concepts."""
    ls = LConcept.nodes.all()
    return [to_model(e) for e in ls]


def delete_concept(uid: UUID) -> None:
    """Delete concept."""
    LConcept.nodes.first(uid=uid.hex).delete()


def change_concept(
    uid: UUID,
    name: str | None = None,
    explain: str | None = None,
) -> Concept:
    """Change concept properties."""
    c = LConcept.nodes.first(uid=uid.hex)
    if name is not None:
        c.name = name
    if explain is not None:
        c.explain = explain
    return to_model(c.save())


def find_one(uid: UUID) -> Concept:
    """Find only one."""
    return to_model(LConcept.nodes.get(uid=uid.hex))


def list_by_pref_uid(pref_uid: str) -> list[LConcept]:
    """uidの前方一致で検索."""
    return LConcept.nodes.filter(uid__startswith=pref_uid)


def complete_concept(pref_uid: str) -> Concept:
    """uuidが前方一致する要素を1つ返す."""
    ls = list_by_pref_uid(pref_uid)
    if len(ls) != 1:
        msg = f"{len(ls)}件がヒットしました: {list(ls)}"
        raise NotUniqueFoundError(msg)
    return to_model(ls[0])
