from datetime import date

from knowde._feature._shared.domain import to_date
from knowde._feature.reference.dto import PartialBookParam
from knowde._feature.reference.repo.book import change_book
from knowde._feature.reference.repo.label import BookUtil


def test_first_edited() -> None:
    b1 = BookUtil.create(title="t1", first_edited=to_date("2024-01-01")).to_model()
    assert b1.first_edited == date(2024, 1, 1)
    b2 = change_book(
        b1.valid_uid,
        PartialBookParam(first_edited=to_date("2024-01-02")),
    )
    assert b2.first_edited == date(2024, 1, 2)
