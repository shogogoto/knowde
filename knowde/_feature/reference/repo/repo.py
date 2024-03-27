from uuid import UUID

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature.reference.domain import Book
from knowde._feature.reference.dto import BookParam

from .label import BookUtil


def add_book(p: BookParam) -> Book:
    if BookUtil.find_one_or_none(title=p.title):
        msg = f"「{p.title}」は既に登録済みです."
        raise AlreadyExistsError(msg)
    return BookUtil.create(title=p.title).to_model()


def remove_book(uid: UUID) -> None:
    book = BookUtil.find_by_id(uid).to_model()
    BookUtil.delete(book.valid_uid)


# def change(uid: UUID, p: BookParam) -> None:
#     book = BookUtil.find_by_id(uid)


# def add_section(p: SectionParam) -> None:
#     pass


# def change_order_of_section() -> None:
#     pass
