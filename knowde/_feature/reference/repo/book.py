from uuid import UUID

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature.reference.domain import Book
from knowde._feature.reference.dto import BookParam, PartialBookParam

from .label import BookUtil


# add and change bookはauthorとの絡みがあるため、
#  advanced featureへ移動するかも
def add_book(p: BookParam) -> Book:
    """同じタイトルでも作者が別なら許容される."""
    if BookUtil.find_one_or_none(title=p.title):
        msg = f"「{p.title}」は既に登録済みです."
        raise AlreadyExistsError(msg)
    return BookUtil.create(title=p.title).to_model()


def remove_book(uid: UUID) -> None:
    """本配下を削除."""
    BookUtil.delete(uid)


def change_book(uid: UUID, p: PartialBookParam) -> Book:
    return BookUtil.change(uid=uid, **p.model_dump()).to_model()
