"""deep search."""


from uuid import UUID

import networkx as nx

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.sentence.domain import Sentence
from knowde._feature.term.domain import Term
from knowde.feature.definition.domain.domain import (
    DefinitionTree,
)
from knowde.feature.definition.repo.definition import RelDefUtil
from knowde.feature.definition.repo.mark import RelMark, RelMarkUtil


def find_recursively(term_uid: UUID) -> DefinitionTree:
    """ある定義に依存するすべての定義を返す.

    定義詳細の一覧性のための機能が１つは欲しい
    複数 MARKとDEFINEを交互に繰り返すパターンを記述できない 20240312
    """
    mn = RelMarkUtil.name
    dn = RelDefUtil.name
    res = query_cypher(
        f"""
        MATCH (t1:Term {{uid: $uid}})
        OPTIONAL MATCH p = (t1)-[:DEFINE]->(:Sentence)
            -[:{mn}|{dn}]->*(:Term)-[:{dn}]->(:Sentence)
        RETURN p
        """,
        params={"uid": term_uid.hex},
    )
    g = nx.DiGraph()
    for elm in res.get("p"):
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
    return DefinitionTree(root_term_uid=term_uid, g=g)
