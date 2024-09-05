"""textから章節を抜き出す."""


from knowde.feature.parser.domain.comment import load_with_comment


def test_parse_heading_with_comment() -> None:
    """コメント付き章の抽象木を抜き出す."""
    s = r"""
        ## H2
        ! c1
        ! c2
        ### H3
        ! c3
        ! c4
        ! c5
        ## H4
    """

    cd = load_with_comment(s)
    assert cd.strs("H2") == ["c1", "c2"]
    assert cd.strs("H3") == ["c3", "c4", "c5"]
    assert cd.strs("H4") == []
