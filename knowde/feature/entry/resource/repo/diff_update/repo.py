"""repo."""

from pprint import pp

from neomodel import adb

from knowde.feature.entry.label import LResource
from knowde.feature.entry.resource.repo.diff_update.cypher import (
    build_varnames,
    delete_sentency_qs,
    delete_term_qs,
    insert_term_q,
    match_nodes,
    match_rel_for_del,
    merge_edge_q,
    update_sentence_q,
)
from knowde.feature.entry.resource.repo.diff_update.domain.builder import (
    build_sentency_updiff,
    build_term_updiff,
)
from knowde.feature.entry.resource.repo.diff_update.domain.domain import (
    diff2sets,
    edges2nodes,
    sysnet2edges,
)
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.entry.resource.repo.save import q_create_node, t2labels
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.types import UUIDy, to_uuid


# 単文のuidをなるべく不変にする
async def update_resource_diff(
    resource_id: UUIDy,
    upd: SysNet,
    do_print: bool = False,  # noqa: FBT001, FBT002
):
    """更新差分の反映."""
    sn, uids = await restore_sysnet(resource_id)
    rm_s, add_s, upd_s = build_sentency_updiff(sn, upd)
    rm_t, add_t, upd_t = build_term_updiff(sn, upd)
    e_rem, e_add = diff2sets(sysnet2edges(sn), sysnet2edges(upd))
    varnames = build_varnames(
        sn,
        upd,
        rm_t | set(upd_t.keys()),
        add_t | set(upd_t.values()),
        rm_s | set(upd_s.keys()) | edges2nodes(e_rem),
        add_s | set(upd_s.values()) | edges2nodes(e_add),
    )

    if do_print:
        print("#" * 30)  # noqa: T201
        pp(varnames)
        print(f"{rm_s =}")  # noqa: T201
        print(f"{add_s =}")  # noqa: T201
        print(f"{upd_s =}")  # noqa: T201
        print(f"{rm_t =}")  # noqa: T201
        print(f"{add_t =}")  # noqa: T201
        print(f"{upd_t =}")  # noqa: T201
        print(f"{e_rem =}")  # noqa: T201
        print(f"{e_add =}")  # noqa: T201

    def build_query() -> list[str]:  # local varsを減らす
        q_delrels, var_delrels = match_rel_for_del(e_rem, varnames)
        t_for_del = rm_t | set(upd_t.keys())
        match_t, q_t_del = delete_term_qs(t_for_del, varnames, sn)

        new2old = {v: k for k, v in upd_s.items()}
        qs = [
            f"MATCH (root:{t2labels(LResource)} {{uid: $uid}})",
            *match_nodes(varnames, uids),
            *match_t,
            *q_delrels,
            *q_t_del,
            *delete_sentency_qs(rm_s, varnames),
            *[q_create_node(n, varnames) for n in add_s],
            *[merge_edge_q(e, varnames, new2old) for e in e_add],
            *[f"DELETE {r}" for r in var_delrels],
            *[
                insert_term_q(t, varnames, upd, new2old)
                for t in add_t | set(upd_t.values())
            ],
            *[update_sentence_q(o, n, varnames) for o, n in upd_s.items()],
        ]
        return [q for q in qs if q is not None]

    qs = build_query()
    if len(qs) == 1:  # 規定のroot matchだけで更新なし
        return

    query = "\n".join(qs)
    if do_print:
        print("-" * 30)  # noqa: T201
        print(query)  # noqa: T201

    await adb.cypher_query(
        query,
        params={"uid": to_uuid(resource_id).hex},
    )
