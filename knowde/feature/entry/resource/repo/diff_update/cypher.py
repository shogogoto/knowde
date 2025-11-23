"""cypher文作成."""

from collections.abc import Iterable
from uuid import UUID

from knowde.feature.entry.resource.repo.save import q_create_node
from knowde.feature.parsing.sysnet.sysnode import KNode
from knowde.shared.types import to_uuid


def q_update_added(added: Iterable[KNode]) -> str:
    """単文追加."""
    q = ""
    varnames = {n: f"n{i}" for i, n in enumerate(added)}
    for a in added:
        q += f"{q_create_node(a, varnames)}\n"
    return q


def q_update_removed(removed: Iterable[KNode]) -> str:
    """単文削除."""
    q = ""
    varnames = {n: f"n{i}" for i, n in enumerate(removed)}
    for r in removed:
        q += f"MATCH (n) WHERE id(n) = id({varnames[r]}) DETACH DELETE n\n"
    return q


def match_qs(varnames: dict[KNode, str], uids: dict[KNode, UUID]) -> list[str]:
    """差分更新のために既存ノードをマッチさせる."""
    qs = []

    for n, name in varnames.items():
        uid = uids.get(n)
        if uid is not None:
            q = f"MATCH ({name}:Sentence {{uid: '{to_uuid(uid).hex}'}})"
            qs.append(q)
    return qs
