"""test.

# 文字列変換 from str to date
1000   年だけ
1000/12 年月まで
100/1/1 ゼロ含まない
100/01/01 ゼロ含む
BC200 紀元前
M3/10   明治  和暦対応 datetimejp
S50/11/11 昭和
H20/12/12 平成
R5/01/01 令和

[BC|AD] [-]yyyy[/MM[/dd]]
or
100C [世紀として扱う]
16億年前 -16

yyyy/MM/dd
yyyy/MM
yyyy
yyy
yy
y
yC 世紀
BCy 紀元前
 e

"""


import pytest
from dateutil import parser

from knowde.primitive.time.time import align_yyyyMMdd


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        # yyyy/MM/dd
        ("1000/1/1", "1000-01-01"),
        ("1000/01/1", "1000-01-01"),
        ("1000/1/01", "1000-01-01"),
        ("1000/01/01", "1000-01-01"),
        # yyyy-MM-dd
        ("1000-1-1", "1000-01-01"),
        ("1000-01-1", "1000-01-01"),
        ("1000-1-01", "1000-01-01"),
        ("1000-01-01", "1000-01-01"),
        # yyyy/M
        ("1000-01", "1000-01"),
        ("1000-1", "1000-01"),
        # yyyy
        ("1000", "1000"),
        ("500", "0500"),
        ("50", "0050"),
        ("5", "0005"),
        ("-5", "-005"),
        # 世紀 yyC
        ("-50", ""),
        # 前半early/後半Late/半ばMid
    ],
)
def test_align_timestr(string: str, expected: str) -> None:
    """時系列文字列."""
    _d = parser.parse(string, yearfirst=True, ignoretz=True)

    # print(f"{string} --> ", d)
    assert align_yyyyMMdd(string) == expected


# def test_to_datetime() -> None:
#     pass


# def test_span() -> None:
#     """時間幅."""
#     t = Time("-1000")
#     print(t)
