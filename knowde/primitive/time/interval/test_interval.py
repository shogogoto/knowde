"""test.

# 期間
暗黙の期間 ex. 1000 -> 1000/01/01 ~ 1000/12/31 みたいな
# 月の期間を定義
from dateutil.relativedelta import relativedelta python-dateutil
month_start = year_month.replace(day=1)
month_end = month_start + relativedelta(months=1, days=-1)
明示的期間
    1000/1/1 ~  終わりが不定
    ~ 1111/11/11  始まりが不定
    1000/1/1 ~ 1111/11/11 決まってる



"""


import pytest

from knowde.primitive.time.interval import parse_when


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("1000 ~", "1000/.."),
        ("~ 1200", "../1200"),
        ("1000 ~ 1200", "1000/1200"),
        ("1200~", "1200~"),
        ("1200 ~ 1300/12/1", "1200/1300-12-01"),
    ],
)
def test_interval(string: str, expected: str) -> None:
    """EDTFではなく独自のInterval."""
    when = parse_when(string)
    ex = parse_when(expected)
    assert when.lower_strict() == ex.lower_strict()
    assert when.upper_strict() == ex.upper_strict()
