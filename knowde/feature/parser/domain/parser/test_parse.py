"""parser pre処理."""
from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.statement import scan_statements


def test_parse_multiline() -> None:
    """改行ありで一行とみなす."""
    _s = r"""
        # src
            ! multiline
            aaa_\
            bbb
                ccc
                cccc
            ddd
            mul1 \
                mul2 \
                    mul3
    """
    t = transparse(_s)
    assert scan_statements(t) == [
        "aaa_bbb",
        "ccc",
        "cccc",
        "ddd",
        "mul1 mul2 mul3",
    ]
