"""隣接クエリ関連."""

from enum import StrEnum

from knowde.shared.nxutil.edge_type import EdgeType


def detail_match(sent_var: str, dist: int | None) -> str:
    """隣接する文のIDを返す."""
    if dist == 1:
        return f"""
        // 1個下の兄弟まで
        OPTIONAL MATCH ({sent_var})-[:BELOW]->(detail1:Sentence)
        OPTIONAL MATCH (detail1)-[:SIBLING]->*(detail2:Sentence)
        UNWIND [detail1, detail2] AS detail
    """
    d = "" if dist is None else str(dist)
    return f"""
        OPTIONAL MATCH ({sent_var})-[:BELOW]->(:Sentence)
            -[:SIBLING|BELOW]->{{0, {d}}}(detail:Sentence)
    """


def q_arrow(name: str, reverse: bool) -> str:  # noqa: FBT001
    """矢印."""
    return f"<-[:{name}]-" if reverse else f"-[:{name}]->"


class AdjType(StrEnum):
    """隣接タイプ (HTTP/FastAPI互換)."""

    PREMISE = "premise"
    CONCLUSION = "conclusion"
    REFERRED = "referred"
    REFER = "refer"
    ABSTRACT = "abstract"
    EXAMPLE = "example"
    DETAIL = "detail"

    @property
    def reverse(self) -> bool:
        """arrowの向きを逆にするか."""
        return self in {AdjType.PREMISE, AdjType.REFERRED, AdjType.ABSTRACT}

    @property
    def edge_type(self) -> EdgeType:
        """EdgeType."""
        return {
            AdjType.PREMISE: EdgeType.TO,
            AdjType.CONCLUSION: EdgeType.TO,
            AdjType.REFERRED: EdgeType.RESOLVED,
            AdjType.REFER: EdgeType.RESOLVED,
            AdjType.ABSTRACT: EdgeType.EXAMPLE,
            AdjType.EXAMPLE: EdgeType.EXAMPLE,
            AdjType.DETAIL: EdgeType.BELOW,
        }[self]

    def match(self, sent_var: str, dist: int | None) -> str:
        """Match query."""
        if self == AdjType.DETAIL:
            return detail_match(sent_var, dist)
        name, rev, et = self.value, self.reverse, self.edge_type
        ar = q_arrow(et.name, rev)
        d = "" if dist is None else str(dist)
        return f"""
        OPTIONAL MATCH ({sent_var}){ar}{{1,{d}}}({name}:Sentence)"""

    @property
    def collect(self) -> str:
        """uuid集計."""
        name = self.value
        return f"""
            , COLLECT(DISTINCT {name}.uid) AS {name}s"""
