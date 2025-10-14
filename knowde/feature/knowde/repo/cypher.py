"""cypherの組立て."""

from collections.abc import Callable
from textwrap import indent
from typing import Any, Final

from more_itertools import first_true
from neo4j.graph import Path

from knowde.feature.entry.mapper import MResource
from knowde.feature.knowde import LocationWithoutParents, UidStr
from knowde.feature.knowde.repo.clause import OrderBy, WherePhrase
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.user.schema import UserReadPublic


def q_indent(f: Callable) -> Callable:
    """インデントデコレータ."""

    def wrapper(*args, **kwargs):
        return indent(f(*args, **kwargs), " " * 2)

    return wrapper


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
        CALL ({tgt}) {{
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
                {(order_by.score_prop() if order_by else "")}
            }} AS stats
        }}
        """
    )


def q_call_sent_names(var: str) -> str:
    """単文の名前を取得."""
    return f"""
    CALL ({var}) {{
        OPTIONAL MATCH ({var})<-[r:DEF]-(t1:Term)
        OPTIONAL MATCH p = (t1)-[:ALIAS]->*(t2:Term)
        WITH p, LENGTH(p) as len, r
        ORDER BY len DESC
        LIMIT 1
        RETURN nodes(p) as names
            , r.alias AS alias
    }}
    """


@q_indent
def q_where_knowde(p: WherePhrase = WherePhrase.CONTAINS) -> str:
    """検索文字列が含まれている文と用語に紐づく文を返す."""
    where_phrase = f"{p.value} $s"
    return f"""
        // 検索文字列が含まれる文
        MATCH (sent1: Sentence WHERE sent1.val {where_phrase})
        {q_call_sent_names("sent1")}
        RETURN sent1 as sent, names
        UNION
        // 検索文字列が含まれる用語
        MATCH (term2: Term WHERE term2.val {where_phrase}),
        (n1)-[:ALIAS]-*(term2: Term)-[:ALIAS]-*(n2: Term)
            -[:DEF]->(sent3: Sentence)
        UNWIND [n2, n1] as name3
        RETURN sent3 as sent, COLLECT(DISTINCT name3) as names
    """


def q_adjaceny_uids(sent_var: str) -> str:
    """隣接する文のIDを返す."""
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


# resourceに至るには SIBLING|BELOW|HEAD(|NUM) のみを辿れば良い
#  これをstream と呼ぶ
# これ以外では 無方向でアスタによる高コストな 複雑関係 EXAMPLE|TO|RESOLVED
#   で対称のsentenceまでのpathを取得する
# この complex の端以外では stream は現れない、として曖昧さ・検索コストを減らす
#  (r:Resource)-[stream]->*(:Sentence)-[complex]-(:Sentence)
# (:Resource)--*(sent) ではコスト高すぎるかも
#

STREAM: Final = "SIBLING|BELOW|NUM|BY"


def q_upper(sent_var: str) -> str:
    """parentの末尾 upper を取得する."""
    # RESOLVED は含めない ブロックを飛び越えて広範囲に探索することになって
    #   応答が返ってこなくなる
    complex_ = "TO|EXAMPLE"  # resourceに近づくとは限らない方向
    return f"""
        CALL ({sent_var}) {{
            // Resource直下でも許容
            MATCH (r:Resource {{uid: {sent_var}.resource_uid}})
            OPTIONAL MATCH p = (r)-[:{STREAM}]->*
                (_upper:Sentence|Head)-[:{STREAM}]->
                (up:Sentence)
                , (up)-[:{complex_}|NUM|BY]-*({sent_var})
            WITH p, LENGTH(p) as len, up, _upper, r
            ORDER BY len ASC // 最短
            LIMIT 1
            RETURN CASE
                WHEN up IS NOT NULL THEN up
                WHEN _upper IS NOT NULL THEN _upper
                ELSE {sent_var}
            END AS upper
                , r AS resource
        }}
    """


def q_location(sent_var: str) -> str:
    """位置情報."""
    return f"""
    CALL ({sent_var}) {{
        {q_upper(sent_var)}
        OPTIONAL MATCH p2 = (resource)-[:{STREAM}]->*(upper)
        , p = (user:User)<-[:OWNED|PARENT]-*(resource)
        RETURN nodes(p) + p2 AS location
    }}
    """


def build_location_res(
    row: Any,
    self_uid: str,
) -> tuple[LocationWithoutParents, list[str]]:
    """locationのレコードからmodelを組み立てる."""
    row = list(dict.fromkeys(row))
    user = UserReadPublic.model_validate(dict(row[0]), by_alias=True)
    r = first_true(row[1:], pred=lambda n: "Resource" in n.labels)
    i_r = row.index(r)

    path: Path = row[i_r + 1]  # リソース ~ 文のパス
    heads = [
        rel.end_node for rel in path.relationships if "Head" in rel.end_node.labels
    ]
    headers = [UidStr(val=e.get("val"), uid=e.get("uid")) for e in heads]
    parent_uids = [
        rel.start_node.get("uid")
        for rel in path.relationships
        if rel.type == "BELOW" and "Sentence" in rel.start_node.labels
    ]
    if self_uid in parent_uids:
        parent_uids.remove(self_uid)
    return LocationWithoutParents(
        user=user,
        folders=[UidStr(val=e.get("name"), uid=e.get("uid")) for e in row[1:i_r]],
        resource=MResource.freeze_dict(dict(r)),
        headers=headers,
    ), list(dict.fromkeys(parent_uids))
