"""クイズ共通のテスト用データ."""

from knowde.feature.entry.resource.usecase import save_text
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister


async def fx_u() -> LUser:  # noqa: D103
    user = await aregister(email="quiz@ex.com")
    u: LUser = await LUser.nodes.get(email=user.email)
    u.username = "quiz"
    await u.save()
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
    _sn, _m = await save_text(user.uid, s)
    return user
