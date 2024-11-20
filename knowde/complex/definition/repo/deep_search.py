"""deep search."""
from uuid import UUID

import networkx as nx

from knowde.complex.definition.domain.domain import (
    Definition,
    DefinitionTree,
)
from knowde.complex.definition.repo.definition import RelDefUtil
from knowde.complex.definition.repo.mark import RelMark, RelMarkUtil
from knowde.complex.definition.sentence.domain import Sentence
from knowde.complex.definition.term.domain import Term
from knowde.core.label_repo.query import query_cypher


def find_recursively(def_uid: UUID) -> DefinitionTree:
    """ある定義に依存するすべての定義を返す.

    定義詳細の一覧性のための機能が１つは欲しい
    複数 MARKとDEFINEを交互に繰り返すパターンを記述できない 20240312
    """
    mn = RelMarkUtil.name
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH (t1:Term)-[def:{dn} {{uid: $uid}}]->(s:Sentence)
        OPTIONAL MATCH p = (s)-[:{mn}|{dn}]->*(:Term)-[:{dn}]->(:Sentence)
        RETURN p, def
        """,
        params={"uid": def_uid.hex},
    )
    g = nx.DiGraph()

    rel = next(iter(res.get("def")))
    d = Definition.from_rel(rel)
    g.add_edge(d.term, d.sentence, rel=rel)

    for elm in res.get("p"):
        if elm is None:
            continue
        for rel in elm.relationships:
            start = rel.start_node()
            end = rel.end_node()
            if not isinstance(rel, RelMark):  # DEFINE
                n1 = Term.to_model(start)
                n2 = Sentence.to_model(end)
            else:  # MARK (:Sentence) -> (:Term)
                n1 = Sentence.to_model(start)
                n2 = Term.to_model(end)
            g.add_edge(n1, n2, rel=rel)
    return DefinitionTree(root_term_uid=d.term.valid_uid, g=g)
