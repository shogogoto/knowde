"""test."""
import pytest

from knowde.primitive.time.time import parse_time, str2edtf


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
        # 紀元前
        ("BC200", "-0200"),
        ("BC200/12", "-0200-12"),
        ("BC200/12/12", "-0200-12-12"),
        # 世紀 yyC
        ("20C", "1901/2000"),
        ("-20C", "-1999/-1900"),
        ("-3C", "-0299/-0200"),
        ("BC2C", "-0199/-0100"),
        ("-2C", "-0199/-0100"),
        # 4桁以上
        ("-50000", "Y-50000"),
        ("50000", "Y50000"),
    ],
)
def test_2edtf(string: str, expected: str) -> None:
    """EDTFへの通常パターン."""
    aligned = str2edtf(string)
    assert aligned == expected
    parse_time(aligned)  # not raise exception


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        # 前半early/後半Late/半ばMid
        # 和暦
        # M3/10   明治  和暦対応 datetimejp
        # S50/11/11 昭和
        # H20/12/12 平成
        # R5/01/01 令和.
    ],
)
def test_2edtf_try(string: str, expected: str) -> None:
    """独自のEDTF変換形式."""
    # print("-" * 30, string, expected)
    # print("-" * 30, string, expected)
    # print("-" * 30, string, expected)
    assert str2edtf(string) == expected
    # t = parse_time(expected)
    # print(t)

    # print(t.lower_strict())
    # print(t.upper_strict())
