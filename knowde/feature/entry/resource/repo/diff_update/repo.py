"""repo."""

from functools import partial

from neomodel import adb

from knowde.feature.entry.label import LResource
from knowde.feature.entry.resource.repo.diff_update.cypher import (
    match_qs,
    match_rel_for_del,
)
from knowde.feature.entry.resource.repo.diff_update.domain import (
    create_updatediff,
    diff2sets,
    edges2nodes,
    identify_updatediff_txt,
    sysnet2edges,
)
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.entry.resource.repo.save import q_create_node, rel2q, t2labels
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.types import UUIDy, to_uuid


async def update_resource_diff(
    resource_id: UUIDy,
    upd: SysNet,
    do_print: bool = False,  # noqa: FBT001, FBT002
):
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
    sn, uids = await restore_sysnet(resource_id)

    f = partial(identify_updatediff_txt, threshold_ratio=0.6)
    removed, added, updated = create_updatediff(sn.sentences, upd.sentences, f)

    e_rem, e_add = diff2sets(sysnet2edges(sn), sysnet2edges(upd))
    nodes = removed | added | set(updated.keys()) | edges2nodes(e_add)
    varnames = {n: f"n{i}" for i, n in enumerate(nodes)}

    match_dels, var_rels = match_rel_for_del(e_rem, varnames)
    qs = [
        f"MATCH (root:{t2labels(LResource)} {{uid: $uid}})",
        *match_qs(varnames, uids),
        *match_dels,
        *[q_create_node(n, varnames) for n in added],
        *[rel2q(e, varnames) for e in e_add],
        *[f"DELETE {r}" for r in var_rels],
    ]
    query = "\n".join([q for q in qs if q is not None])

    if do_print:
        print("-" * 30)  # noqa: T201
        print(query)  # noqa: T201
    _ = await adb.cypher_query(
        query,
        params={"uid": to_uuid(resource_id).hex},
    )
