"""cypherの組立て."""

from enum import Enum

from pydantic import BaseModel, Field


def q_stats(tgt: str):
    """関係統計の取得cypher."""
    return f"""
        OPTIONAL MATCH ({tgt})<-[:TO]-{{1,}}(premise:Sentence)
        OPTIONAL MATCH ({tgt})-[:TO]->{{1,}}(conclusion:Sentence)
        OPTIONAL MATCH p_leaf = ({tgt})-[:TO]->{{1,}}(leaf:Sentence)
            WHERE NOT (leaf)-[:TO]->(:Sentence)
        OPTIONAL MATCH p_axiom = (axiom:Sentence)-[:TO]->{{1,}}({tgt})
            WHERE NOT (:Sentence)-[:TO]->(axiom)
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


class WherePhrase(Enum):
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

    def query(self) -> str:
        """1ページから始まる."""
        return f"""
        SKIP {self.skip} LIMIT {self.size}
        """


def q_sorting() -> str:
    """OrderBy句の作成."""
    return """



    """
