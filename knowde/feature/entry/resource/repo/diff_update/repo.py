"""repo."""

from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.types import UUIDy


async def update_resource_diff(resource_id: UUIDy, upd: SysNet):
    """更新差分の反映.

    更新箇所の特定
    oldの更新uid を更新後文字列の対

    更新差分domainの表現
    新規 edge は必ず付属
      既存uid + 新規edge + 更新文字列

    既存 uid, 更新文字列

    edgeだけの差し替えもあり得る

    term の更新
    sentenceの更新

    新規node作成の場合
    edgeの更新 旧edgeを真nodeにcopyして旧nodeを削除
    """
    # リソースの全データを取ってくるのは重いかもしれない
    _old, _uids = await restore_sysnet(resource_id)
