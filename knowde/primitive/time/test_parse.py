"""test."""
import pytest

from knowde.primitive.time.time import parse_time, str2edtf


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
        # 前半early/後半Late/半ばMid
        ("19C EARLY", "1900-37"),
        ("19C MID", "1900-38"),
        ("19C LATE", "1900-39"),
    ],
)
def test_2edtf(string: str, expected: str) -> None:
    """EDTFへの通常パターン."""
    # print("-" * 30)
    aligned = str2edtf(string)
    assert aligned == expected
    parse_time(aligned)  # not raise exception


@pytest.mark.parametrize(
    ("string", "expected"),
    [
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
    # s = str2edtf(string)
    # print(f"{s =}")
    assert str2edtf(string) == expected
    # t = parse_time(expected)
    # print(t)

    # print(t.lower_strict())
    # print(t.upper_strict())


# rf. https://www.loc.gov/standards/datetime/
@pytest.mark.parametrize(
    ("string"),
    [
        # Level0
        "1985-04-12",
        "1985-04",
        "1985",
        "1985-04-12T23:20:30",  # こんな形式は使わないだろうな
        ## interval
        "1964/2008",
        "1985-04-12/..",
        "1985-04/..",
        "1985/..",
        "../1985-04-12",
        "../1985-04",
        "../1985",
        "-1111/1000",
        "-1111/..",
        "-1111-11/1000",
        "-1111-11-11/1000",
        "-1111/-1000",
        "../-1000",
        "-1111/-1000-10",
        "-1111/-1000-10-10",
        "-1111-11/-1000-10-10",
        "-1111-11-11/-1000-10-10",
        # Level1
        "1984?",  # uncertain
        "2004-06~",  # approximate
        "2004-06-11%",  # both
        "2004-02-01/2005-02-08",
        "19XX",
        "-19XX",
        "Y50000",
        "[1667,1668,1670..1672]",
    ],
)
def test_already_edtf(string: str) -> None:
    """既にEDTFのものはそのまま."""
    s = str2edtf(string)
    _t = parse_time(s)  # not raise exception
    # print("-" * 10, string)
    # print(t.lower_strict())
    # print(t.upper_strict())
    assert s == string
