"""repo."""

from collections.abc import Iterable
from functools import partial
from pprint import pp

from neomodel import adb

from knowde.feature.entry.label import LResource
from knowde.feature.entry.resource.repo.diff_update.cypher import (
    delete_term_qs,
    insert_term_q,
    match_nodes,
    match_rel_for_del,
    merge_edge_q,
    update_sentence_q,
)
from knowde.feature.entry.resource.repo.diff_update.domain import (
    create_updatediff,
    diff2sets,
    edges2nodes,
    get_switched_def_terms,
    identify_duplicate_updiff,
    identify_updatediff_term,
    identify_updatediff_txt,
    sysnet2edges,
)
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.entry.resource.repo.save import q_create_node, t2labels
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import Def, Sentency
from knowde.shared.types import UUIDy, to_uuid


# db操作以外はdomainに移す
# 単文のuidをなるべく不変にする
async def update_resource_diff(  # noqa: PLR0914
    resource_id: UUIDy,
    upd: SysNet,
    do_print: bool = False,  # noqa: FBT001, FBT002
):
    """更新差分の反映."""
    sn, uids = await restore_sysnet(resource_id)

    # 単文
    def f1(old: Iterable[Sentency], new: Iterable[Sentency]):
        updiff = identify_updatediff_txt(
            [o for o in old if isinstance(o, str)],
            [n for n in new if isinstance(n, str)],
            threshold_ratio=0.6,
        )
        updiff |= identify_duplicate_updiff(sn, upd)
        return updiff

    removed, added, updated = create_updatediff(sn.sentences, upd.sentences, f1)
    # 用語
    f2 = partial(identify_updatediff_term, threshold_ratio=0.6)
    rm_t, add_t, upd_t = create_updatediff(sn.terms, upd.terms, f2)
    # 関係
    e_rem, e_add = diff2sets(sysnet2edges(sn), sysnet2edges(upd))

    # 定義の組み合わせの変更のみを取得
    switched_t = get_switched_def_terms(sn, upd)
    upd_t |= switched_t

    # 用語の変更分からの定義
    defs = {sn.get(t) for t in rm_t | upd_t.keys()} | {
        upd.get(t) for t in add_t | set(upd_t.values())
    }
    sentences = (
        removed
        | added
        | set(updated.keys())
        | edges2nodes(e_add)
        | {d.sentence for d in defs if isinstance(d, Def)}
    )
    varnames = {sent: f"n{i}" for i, sent in enumerate(sentences)}

    if do_print:
        print("#" * 30)  # noqa: T201
        print(f"{removed =}")  # noqa: T201
        print(f"{added =}")  # noqa: T201
        print(f"{updated =}")  # noqa: T201
        print(f"{defs}")  # noqa: T201
        pp(varnames)
        print(f"{rm_t =}")  # noqa: T201
        print(f"{add_t =}")  # noqa: T201
        print(f"{upd_t =}")  # noqa: T201
        # print(f"{e_rem =}")
        # print(f"{e_add =}")
        print(f"{switched_t =}")  # noqa: T201

    # クエリ構築
    q_delrels, var_delrels = match_rel_for_del(e_rem, varnames)
    t_for_del = rm_t | set(upd_t.keys())
    match_t, q_t_del = delete_term_qs(t_for_del, varnames, sn)

    new2old = {v: k for k, v in updated.items()}
    new_t = add_t | set(upd_t.values())

    qs = [
        f"MATCH (root:{t2labels(LResource)} {{uid: $uid}})",
        *match_nodes(varnames, uids),
        *match_t,
        *q_delrels,
        *q_t_del,
        *[q_create_node(n, varnames) for n in added],
        *[f"DELETE {r}" for r in var_delrels],
        *[merge_edge_q(e, varnames, new2old) for e in e_add],
        *[insert_term_q(t, varnames, upd, new2old) for t in new_t],
        *[update_sentence_q(o, n, varnames) for o, n in updated.items()],
    ]
    qs = [q for q in qs if q is not None]
    query = "\n".join(qs)

    if do_print:
        print("-" * 30)  # noqa: T201
        print(query)  # noqa: T201

    if len(qs) == 1:  # 規定のroot matchだけ。他のクエリがない
        return

    _ = await adb.cypher_query(
        query,
        params={"uid": to_uuid(resource_id).hex},
    )
