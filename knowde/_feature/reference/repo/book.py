from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature.reference.domain import Book  # noqa: TCH001
from knowde._feature.reference.dto import BookParam, PartialBookParam  # noqa: TCH001

from .label import BookUtil


# add and change bookはauthorとの絡みがあるため、
#  advanced featureへ移動するかも
def add_book(p: BookParam) -> Book:
    """同じタイトルでも作者が別なら許容される."""
    if BookUtil.find_one_or_none(title=p.title):
        msg = f"「{p.title}」は既に登録済みです."
        raise AlreadyExistsError(msg)
    return BookUtil.create(**p.model_dump()).to_model()


def change_book(ref_uid: UUID, p: PartialBookParam) -> Book:
    return BookUtil.change(uid=ref_uid, **p.model_dump()).to_model()


def complete_book(pref_uid: str) -> Book:
    return BookUtil.complete(pref_uid).to_model()
