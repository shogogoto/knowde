"""cypher文作成."""

from collections.abc import Iterable
from uuid import UUID

from knowde.feature.entry.resource.repo.save import EdgeRel, q_create_node
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import Def, KNode
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


# uid特定はmatch_qsで済んでいる想定
def match_rel_for_del(
    rels: Iterable[EdgeRel],
    varnames: dict[KNode, str],
) -> tuple[list[str], list[str]]:
    """関係を削除."""
    qs = []
    vars_rel = []
    for i, rel in enumerate(rels):
        u, v, t = rel
        var_u = varnames[u]
        var_v = varnames[v]
        var_rel = f"rel{i}"
        q = f"MATCH ({var_u}) -[{var_rel}:{t.arrow}]-> ({var_v})"
        vars_rel.append(var_rel)
        qs.append(q)
    return qs, vars_rel


def delete_term_qs(
    terms: Iterable[Term],
    varnames: dict[KNode, str],
    sn: SysNet,
) -> tuple[list[str], list[str]]:
    """termの更新."""
    q_rels = []
    q_dels = []
    for t in terms:
        df = sn.get(t)
        if not isinstance(df, Def):
            raise TypeError
        var = varnames[df.sentence]
        q = f"MATCH (term_{var}:Term)-[:DEF|ALIAS]-*({var})"
        d = f"DETACH DELETE term_{var}"
        q_rels.append(q)
        q_dels.append(d)
    return q_rels, q_dels


def insert_term_q(
    term: Term,
    varnames: dict[KNode, str],
    sn: SysNet,
) -> list[str]:
    """termの登録."""
    df = sn.get(term)
    if not isinstance(df, Def):
        raise TypeError
    var = varnames[df.sentence]
    q = f"CREATE ({var})<-[:DEF]-(:Term {{val: '{term.names[0]}'}})"
    for name in term.names[1:]:
        q += f"-[:ALIAS]->(:Term {{val: '{name}'}})"
    return q
