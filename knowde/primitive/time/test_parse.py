"""test."""
# ruff: noqa
import pytest

from knowde.primitive.time.time import align4edtf


def test_aaa() -> None:
    """Test."""

    # s = "2000-10-10"
    # dt1 = datetime.fromisoformat(s)
    # dt2 = parse_time(s)
    # print(dt1)
    # print(dt1.timestamp())
    # print(dt2, type(dt2))
    # st = dt2.lower_strict()
    # print(struct_time_to_jd(st))
    # print(struct_time_to_jd(st))
    # print(datetime_to_jd(dt1))
    # print(struct_time_to_jd(dt2))
    # print(struct_time_to_jd(dt2))
    # print(struct_time_to_jd(dt2))
    # print(struct_time_to_jd(dt2))

    # from dateutil import parser

    # # 紀元前の日付を解析する
    # date_str = "200 BC"
    # date = parser.parse(date_str, yearfirst=True, ignoretz=True)


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
        ("-5", "-0005"),
        ("-50", "-0050"),
        ("-500", "-0500"),
        ("-9999", "-9999"),
        # 4桁以上
        # ("Y-5E4", "Y-5E4"),
        # ("-50000", "Y-5E4"),
        # 世紀 yyC
        # 前半early/後半Late/半ばMid
    ],
)
def test_align_timestr(string: str, expected: str) -> None:
    """時系列文字列."""
    # value = ""123.456789
    # print(f"{value:.2e}")  # 小数点以下2桁までの指数表記で表示します。
    # t = parse_time(string)
    # print(t.lower_strict())
    # print(t.upper_strict())
    aligned = align4edtf(string)
    assert aligned == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [],
)
def test_convert_yearstr(string: str, expected: str) -> None:
    """年の様々な表現の変換.

    # 文字列変換 from str to date
    BC200 紀元前
    M3/10   明治  和暦対応 datetimejp
    S50/11/11 昭和
    H20/12/12 平成
    R5/01/01 令和.

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
    """


# def test_to_datetime() -> None:
#     pass


# def test_span() -> None:
#     """時間幅."""
#     t = Time("-1000")
#     print(t)
