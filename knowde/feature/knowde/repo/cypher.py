"""cypherの組立て."""

from enum import StrEnum

from pydantic import BaseModel, Field

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


def q_stats(tgt: str) -> str:
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
        RETURN
          SIZE(premises) AS n_premise
        , SIZE(conclusions) AS n_conclusion
        , MAX(coalesce(length(p_axiom), 0)) AS dist_axiom
        , MAX(coalesce(length(p_leaf), 0)) AS dist_leaf
        , SIZE(referreds) AS n_referred
        , SIZE(refers) AS n_refer
        , SIZE(details) AS n_detail
    """
    )


class WherePhrase(StrEnum):
    """WHERE句の条件."""

    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS WITH"
    ENDS_WITH = "ENDS WITH"
    REGEX = "=~"
    EQUAL = "="


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


class Paging(BaseModel):
    """クエリのページング."""

    page: int = Field(default=1, gt=0)
    size: int = Field(default=100, gt=0)

    @property
    def skip(self) -> int:  # noqa: D102
        return (self.page - 1) * self.size

    def phrase(self) -> str:
        """1ページから始まる."""
        return f"""
        SKIP {self.skip} LIMIT {self.size}
        """


class OrderBy(BaseModel):
    """ORDER BY句.

    weightと項目の合計値(score)でソートできる
    他のスコア算出方法についてはペンディング
    """

    # 元の意味の値ではない
    # weight: KStats = KStats(
    #     n_detail=1,
    #     n_premise=3,
    #     n_conclusion=3,
    #     n_refer=3,
    #     n_referred=-3,
    #     dist_axiom=1,
    #     dist_leaf=1,
    # )

    n_detail: int = 1
    n_premise: int = 1
    n_conclusion: int = 1
    n_refer: int = 1
    n_referred: int = 1
    dist_axiom: int = 1
    dist_leaf: int = 1
    desc: bool = True  # スコアの高い順がデフォルト

    def score_prop(self) -> str:
        """スコアの計算式."""
        qs = []
        prefix = ""
        for k, v in self:
            if v == 0 or k in {"score", "desc"}:  # スコアは省略
                continue
            if v == 1:  # 重み1のときは省略
                qs.append(f"{prefix}{k}")
            else:
                qs.append(f"({v:+} * {prefix}{k})")
        line = " + ".join(qs)
        return f", score: {line}"

    def phrase(self) -> str:
        """ORDER BY句."""
        return f"""
        ORDER BY stats.score {"DESC" if self.desc else "ASC"}
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
