"""時系列.

# CLIで何を表示するか

# 期間
暗黙の期間 ex. 1000 -> 1000/01/01 ~ 1000/12/31 みたいな
# 月の期間を定義
    1000/1/1 ~  終わりが不定
    ~ 1111/11/11  始まりが不定
    1000/1/1 ~ 1111/11/11 決まってる


# **時系列でソート**


    重なった期間をどう表現するか
    intervaltree
        区間の重なり検索が高速
        メモリ効率が良い
        特に期間の重なりチェックに特化
"""
import pytest

from . import Series, parse_when


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


def test_series() -> None:
    """時系列のソート."""
    ser = Series.create(
        [
            "2000/1 ~ 2025",
            "2004/12",
            "1950/7/7",
            "1945",
            "-02XX",
        ],
    )
    assert ser.overlap("2002")[0].data == "2000/1 ~ 2025"
    assert ser.overlap("1945/1/2")[0].data == "1945"
    assert [i.data for i in ser.overlap("2004/12/1")] == ["2000/1 ~ 2025", "2004/12"]
    assert [i.data for i in ser.envelop("2000 ~")] == ["2000/1 ~ 2025", "2004/12"]
    assert [i.data for i in ser.envelop("~ 1949")] == ["-02XX", "1945"]
