"""cypherの組立て."""

from knowde.feature.knowde.repo.clause import OrderBy, WherePhrase
from knowde.shared.nxutil.edge_type import EdgeType


def q_leaf_path(tgt: str, var: str, t: str) -> str:
    """ターゲット方向へのパス."""
    return f"""
        OPTIONAL MATCH {var} = ({tgt}:Sentence)
            -[rel_{var}:{t}]->{{1,}}(leaf_{var}:Sentence)
            WHERE NOT (leaf_{var}:Sentence)-[:TO]->(:Sentence)"""


def q_root_path(tgt: str, var: str, t: str) -> str:
    """ソース方向へのパス."""
    return f"""
        OPTIONAL MATCH {var} = (axiom_{var}:Sentence)-[:{t}]->{{1,}}({tgt})
            WHERE NOT (:Sentence)-[:TO]->(axiom_{var}:Sentence)"""


def q_stats(tgt: str, order_by: OrderBy | None = None) -> str:
    """関係統計の取得cypher."""
    return (
        f"""
        OPTIONAL MATCH ({tgt})<-[:TO]-{{1,}}(premise:Sentence)
        OPTIONAL MATCH ({tgt})-[:TO]->{{1,}}(conclusion:Sentence)
        """
        + q_leaf_path(tgt, "p_leaf", EdgeType.TO.name)
        + q_root_path(tgt, "p_axiom", EdgeType.TO.name)
        + f"""
        OPTIONAL MATCH ({tgt})<-[:RESOLVED]-{{1,}}(referred:Sentence)
        OPTIONAL MATCH ({tgt})-[:RESOLVED]->{{1,}}(refer:Sentence)
        OPTIONAL MATCH ({tgt})-[:BELOW]->(:Sentence)
            -[:SIBLING|BELOW]->*(detail:Sentence)
        WITH COLLECT(DISTINCT premise) as premises
            , COLLECT(DISTINCT conclusion) as conclusions
            , COLLECT(DISTINCT referred) as referreds
            , COLLECT(DISTINCT refer) as refers
            , COLLECT(DISTINCT detail) as details
            , p_axiom
            , p_leaf
        WITH
          SIZE(premises) AS n_premise
        , SIZE(conclusions) AS n_conclusion
        , MAX(coalesce(length(p_axiom), 0)) AS dist_axiom
        , MAX(coalesce(length(p_leaf), 0)) AS dist_leaf
        , SIZE(referreds) AS n_referred
        , SIZE(refers) AS n_refer
        , SIZE(details) AS n_detail
        RETURN {{
            n_premise: n_premise,
            n_conclusion: n_conclusion,
            dist_axiom: dist_axiom,
            dist_leaf: dist_leaf,
            n_referred: n_referred,
            n_refer: n_refer,
            n_detail: n_detail
        """
        + (order_by.score_prop() if order_by else "")
        + """
        } AS stats
        """
    )


def q_sentence_from_def(p: WherePhrase = WherePhrase.CONTAINS) -> str:
    """検索文字列が含まれている文と用語に紐づく文を返す."""
    where_phrase = f"{p.value} $s"
    return f"""
        // 検索文字列が含まれる文
        MATCH (sent1: Sentence WHERE sent1.val {where_phrase})
        OPTIONAL MATCH (term1: Term)-[:DEF|ALIAS]->(sent1)
        OPTIONAL MATCH (term1)-[:ALIAS]-*(name1: Term)
        RETURN sent1 as sent,  COLLECT(name1) as names
        UNION
        // 検索文字列が含まれる用語
        MATCH (term2: Term WHERE term2.val {where_phrase}),
        (n1)-[:ALIAS]-*(term2: Term)-[:ALIAS]-*(n2: Term)
            -[:DEF]->(sent3: Sentence)
        UNWIND [n2, n1] as name3
        RETURN sent3 as sent, COLLECT(DISTINCT name3) as names
    """


def q_adjacent(sent_var: str) -> str:
    """隣接する文を返す."""
    return f"""
        CALL ({sent_var}) {{
            OPTIONAL MATCH ({sent_var})<-[:TO]-(premise:Sentence)
            OPTIONAL MATCH ({sent_var})-[:TO]->(conclusion:Sentence)
            OPTIONAL MATCH ({sent_var})<-[:RESOLVED]-(referred:Sentence)
            OPTIONAL MATCH ({sent_var})-[:RESOLVED]->(refer:Sentence)
            OPTIONAL MATCH ({sent_var})-[:BELOW]->(detail1:Sentence)
            // 近接1階層分だか SIB or BELOW で全てを辿るのではない
            OPTIONAL MATCH (detail1)-[:SIBLING]->*(detail2:Sentence)
            UNWIND [detail1, detail2] as detail
            RETURN
                COLLECT(DISTINCT premise.uid) as premises
                , COLLECT(DISTINCT conclusion.uid) as conclusions
                , COLLECT(DISTINCT referred.uid) as referreds
                , COLLECT(DISTINCT refer.uid) as refers
                , COLLECT(DISTINCT detail.uid) as details
        }}
    """


# def res2adjacent(res: dict[str, Any]) -> KAdjacency:
#     return KAdjacency(
#         uid=res["uid"],
#         n_premise=len(res["premises"]),
#         n_conclusion=len(res["conclusions"]),
#         n_refer=len(res["refers"]),
