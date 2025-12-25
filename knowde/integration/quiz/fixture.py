"""test fixture."""

from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.user.label import LUser


# pytest.fixtureでデコレートしない
#   <- importの補完がでなくなる
#   使用先でpytest.fixureにこれを渡して得た変数を使う
#  ex. sn = pytest.fixture(fx_sn)
def fx_sn() -> SysNet:
    """用語は5個しかない."""
    s = """
        # title
            aaa
            bbb
            parent
                C: ccc
                    T1: ccc1
                    T2: ccc2
                    T3: ccc3
                    -> to
                        T4: todetail
                        -> ccc5
                    <- cccb
                        <- cccb1
    """
    return parse2net(s)


async def fx_u() -> LUser:  # noqa: D103
    user = await LUser(email="quiz@ex.com").save()
    s = """
        # title
            aaa
            bbb
            parent
                C: ccc
                    T1: ccc1
                    T2: ccc2
                    T3: ccc3
                    -> to
                        T4: todetail
                        -> ccc5
                    <- ccca
                    <- cccb
                        <- cccb1
                    ex. ex1
                        ex. ex2
                    xe. ab1
    """
    # T4: todetail -[親]-> parent -[前提]-> ccc が見つかってしまう
    # そんなクイズは非直感的で要らない気がする
    # でもそれは選択肢決定ロジックの責任ということで
    _sn, _m = await save_text(user.uid, s)
    return user
