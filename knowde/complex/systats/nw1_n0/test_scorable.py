"""test."""

from knowde.complex.systats.nw1_n0.scorable import LRWTpl, SyScore
from knowde.complex.systats.nw1_n1.ctxdetail import Nw1N1Label
from knowde.feature.parsing.tree2net import parse2net


def test_scorable_to_edge() -> None:
    """スコアpremise/conclusion."""
    s = """
        # tmp
            aaa
                -> bbb
                -> ccc
                    -> ddd
                        -> eee
                    -> fff
                -> ggg
    """
    sn = parse2net(s)
    items = [Nw1N1Label.PREMISE, Nw1N1Label.CONCLUSION]
    configs = [LRWTpl(Nw1N1Label.PREMISE, 1, 1)]
    ctx = SyScore.create(items, config=configs)
    assert ctx.get_one(sn, "aaa") == {"premise": 0, "conclusion": 3, "score": 3}
    assert ctx.get_one(sn, "bbb") == {"premise": 1, "conclusion": 0, "score": 1}
    assert ctx.get_one(sn, "ccc") == {"premise": 1, "conclusion": 2, "score": 3}
    assert ctx.get_one(sn, "ddd") == {"premise": 1, "conclusion": 1, "score": 2}
    assert ctx.get_one(sn, "eee") == {"premise": 1, "conclusion": 0, "score": 1}
    assert ctx.get_one(sn, "fff") == {"premise": 1, "conclusion": 0, "score": 1}
    assert ctx.get_one(sn, "ggg") == {"premise": 1, "conclusion": 0, "score": 1}

    configs = [LRWTpl(Nw1N1Label.PREMISE, 2, 1)]
    ctx = SyScore.create(items, config=configs)
    assert ctx.get_one(sn, "aaa") == {"premise": 0, "conclusion": 3, "score": 3}
    assert ctx.get_one(sn, "bbb") == {"premise": 1, "conclusion": 0, "score": 1}
    assert ctx.get_one(sn, "ccc") == {"premise": 1, "conclusion": 2, "score": 3}
    assert ctx.get_one(sn, "ddd") == {"premise": 2, "conclusion": 1, "score": 3}
    assert ctx.get_one(sn, "eee") == {"premise": 2, "conclusion": 0, "score": 2}
    assert ctx.get_one(sn, "fff") == {"premise": 2, "conclusion": 0, "score": 2}
    assert ctx.get_one(sn, "ggg") == {"premise": 1, "conclusion": 0, "score": 1}

    configs = [LRWTpl(Nw1N1Label.PREMISE, 3, 2)]
    ctx = SyScore.create(items, config=configs)
    assert ctx.get_one(sn, "aaa") == {"premise": 0, "conclusion": 3, "score": 3}
    assert ctx.get_one(sn, "bbb") == {"premise": 1, "conclusion": 0, "score": 2}
    assert ctx.get_one(sn, "ccc") == {"premise": 1, "conclusion": 2, "score": 4}
    assert ctx.get_one(sn, "ddd") == {"premise": 2, "conclusion": 1, "score": 5}
    assert ctx.get_one(sn, "eee") == {"premise": 3, "conclusion": 0, "score": 6}
    assert ctx.get_one(sn, "fff") == {"premise": 2, "conclusion": 0, "score": 4}
    assert ctx.get_one(sn, "ggg") == {"premise": 1, "conclusion": 0, "score": 2}


def test_scorable() -> None:
    """スコア設定テスト."""
    s = """
        # tmp
            refer referred
            A: a2 0
            B{A}: b2 1
            C{BA}: c2 1
            D{CBA}: d0 1
            E{A}{BA}: {CBA}0 3
    """
    sn = parse2net(s)
    items = [Nw1N1Label.REFER, Nw1N1Label.REFERRED]

    configs = [LRWTpl(Nw1N1Label.REFER, 1, 1)]
    ctx = SyScore.create(items, config=configs)
    assert ctx.get_one(sn, "a2 0") == {"refer": 2, "referred": 0, "score": 2}
    assert ctx.get_one(sn, "b2 1") == {"refer": 2, "referred": 1, "score": 3}
    assert ctx.get_one(sn, "c2 1") == {"refer": 2, "referred": 1, "score": 3}
    assert ctx.get_one(sn, "d0 1") == {"refer": 0, "referred": 1, "score": 1}
    assert ctx.get_one(sn, "{CBA}0 3") == {"refer": 0, "referred": 3, "score": 3}
    assert ctx.get_one(sn, "refer referred") == {
        "refer": 0,
        "referred": 0,
        "score": 0,
    }

    configs = [LRWTpl(Nw1N1Label.REFER, 2, 3)]
    ctx = SyScore.create(items, config=configs)
    assert ctx.get_one(sn, "a2 0") == {"refer": 4, "referred": 0, "score": 12}
    assert ctx.get_one(sn, "b2 1") == {"refer": 4, "referred": 1, "score": 13}
    assert ctx.get_one(sn, "c2 1") == {"refer": 2, "referred": 1, "score": 7}
    assert ctx.get_one(sn, "d0 1") == {"refer": 0, "referred": 1, "score": 1}
    assert ctx.get_one(sn, "{CBA}0 3") == {"refer": 0, "referred": 3, "score": 3}
    assert ctx.get_one(sn, "refer referred") == {
        "refer": 0,
        "referred": 0,
        "score": 0,
    }
