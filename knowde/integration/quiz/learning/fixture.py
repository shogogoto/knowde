"""テスト用データ."""

from knowde.feature.entry.resource.usecase import save_text
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister


async def fx_learning() -> LUser:  # noqa: D103
    user = await aregister(email="quiz@ex.com")
    u: LUser = await LUser.nodes.get(email=user.email)
    u.username = "quiz"
    await u.save()
    s = """
        # title
            A: a
            B: b
            C: c
            D: d
            S: s
                s1
                s2
                <- pre_s
    """
    _sn, _m = await save_text(user.uid, s)
    return user
