"""更新差分repo test.

既存変更
    文字列
    用語
    関係
        below
        sibling
        順番入れ替え

追加
    文字列
    用語
    関係
"""

from knowde.conftest import mark_async_test
from knowde.feature.entry.resource.repo.diff_update.repo import update_resource_diff
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.user.label import LUser


@mark_async_test()
async def test_diff_update_repo() -> None:
    """差分更新repo test."""
    u = await LUser(email="one@gmail.com").save()
    _, rm = await save_text(
        u.uid,
        """
        # title1
          aaa
          bbb
    """,
    )
    new = """
        # title1
            aaa
            bbbb
            ccc
    """
    new_sn = parse2net(new)
    await update_resource_diff(rm.uid, new_sn)

    _sn, _ = await restore_sysnet(rm.uid)
