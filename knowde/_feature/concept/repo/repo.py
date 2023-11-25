"""concept repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature.concept.error import NotUniqueFoundError
from knowde._feature.concept.repo.repo_rel import connect, find_adjacent

from .label import LConcept, to_model

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.concept.domain import Concept
    from knowde._feature.concept.domain.domain import SaveProp
    from knowde._feature.concept.domain.rel import AdjacentConcept


def save_concept(c: SaveProp[str]) -> AdjacentConcept:
    """Create concept."""
    lc = LConcept(**c.model_dump()).save()
    saved = to_model(lc)
    for sid in c.src_ids:
        src = complete_concept(sid)
        connect(src.valid_uid, saved.valid_uid)
    for did in c.dest_ids:
        dest = complete_concept(did)
        connect(saved.valid_uid, dest.valid_uid)
    return find_adjacent(saved.valid_uid)


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
    c = LConcept.nodes.get(uid=uid.hex)
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
    return LConcept.nodes.filter(uid__startswith=pref_uid.replace("-", ""))


def complete_concept(pref_uid: str) -> Concept:
    """uuidが前方一致する要素を1つ返す."""
    ls = list_by_pref_uid(pref_uid)
    if len(ls) != 1:
        msg = f"{len(ls)}件がヒットしました: {list(ls)}"
        raise NotUniqueFoundError(msg)
    return to_model(ls[0])
