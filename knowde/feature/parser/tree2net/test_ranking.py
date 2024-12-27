"""テストケース作るの楽."""


from knowde.feature.parser.tree2net import parse2net


def test_ranking() -> None:
    """用語な文(定義)を降順で取得."""
    _s = r"""
        # h1
            aaa
            B: bbb
                B1: bbb1
                bbb2
                bbb3
            ccc{B}
            `B`
                below2
                below3
            eee{B}
            fff
            G{B}: ggg
    """
    _sn = parse2net(_s)
    # for c in get_ranking(sn):
    #     print(c.rank, c)
