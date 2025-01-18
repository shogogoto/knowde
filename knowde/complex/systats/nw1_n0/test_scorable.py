"""test."""


from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats.nw1_n0.scorable import LRWTpl, SysContexts
from knowde.complex.systats.nw1_n1.ctxdetail import Nw1N1Label
from knowde.feature.__core__.cliutil import echo_table


def test_scorable() -> None:
    """スコア設定テスト."""
    _s = """
        # tmp
            refer referred
            A: a2 0
            B{A}: b2 1
            C{BA}: c2 1
            D{CBA}: d0 1
            E{A}{BA}: {CBA}0 3
    """
    sn = parse2net(_s)
    items = [Nw1N1Label.REFER, Nw1N1Label.REFERRED]

    configs = [LRWTpl(Nw1N1Label.REFERRED, 1, 1)]
    ctx1 = SysContexts.create(items, config=configs)
    assert ctx1.get_one(sn, "a2 0") == {"refer": 2, "referred": 0, "score": 2}
    assert ctx1.get_one(sn, "b2 1") == {"refer": 2, "referred": 1, "score": 3}
    assert ctx1.get_one(sn, "c2 1") == {"refer": 2, "referred": 1, "score": 3}
    assert ctx1.get_one(sn, "d0 1") == {"refer": 0, "referred": 1, "score": 1}
    assert ctx1.get_one(sn, "{CBA}0 3") == {"refer": 0, "referred": 3, "score": 3}
    assert ctx1.get_one(sn, "refer referred") == {
        "refer": 0,
        "referred": 0,
        "score": 0,
    }

    configs = [LRWTpl(Nw1N1Label.REFER, 2, 1)]
    ctx2 = SysContexts.create(items, config=configs)
    echo_table(ctx2.to_json(sn))
    # assert ctx2.get_one(sn, "a2, 0") == {"refer": 2, "referred": 0, "score": 2}
    # assert ctx2.get_one(sn, "b2, 1") == {"refer": 2, "referred": 1, "score": 3}
    # assert ctx2.get_one(sn, "c2, 1") == {"refer": 2, "referred": 1, "score": 3}
    # assert ctx2.get_one(sn, "d0, 1") == {"refer": 0, "referred": 1, "score": 1}
    # assert ctx2.get_one(sn, "{CBA}0, 3") == {"refer": 0, "referred": 3, "score": 3}
    # assert ctx2.get_one(sn, "refer, referred") == {
    #     "refer": 0,
    #     "referred": 0,
    #     "score": 0,
    # }
    # nxprint(sn.g, True)

    # fn = recursively_nw1n1(get_refer, 1)
    # print(fn(sn, "a2 0"))
    # fn = recursively_nw1n1(get_referred, 1)
    # print(fn(sn, "{CBA}0 3"))
    # fn = recursively_nw1n1(get_referred, 2)
    # print(fn(sn, "{CBA}0 3"))
    # fn = recursively_nw1n1(get_referred, 3)
    # print(fn(sn, "{CBA}0 3"))

    # pp([r.to_dict(sn) for r in res])
    # pp(ctx1.to_json(sn))
    # echo_table(ctx1.to_json(sn))
