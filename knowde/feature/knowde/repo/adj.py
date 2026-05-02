"""隣接クエリ関連."""

from enum import Enum

from pydantic import BaseModel

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


class AdjQuery(BaseModel, frozen=True):
    """隣接タイプ."""

    reverse: bool = False
    sent_var: str  # 単文変数名
    dist: int | None = None
    name: str
    et: str

    @property
    def match(self) -> str:
        """Match query."""
        sv = self.sent_var
        d = "" if self.dist is None else str(self.dist)
        arrow = q_arrow(self.et, self.reverse)
        name = self.name
        return f"""
        OPTIONAL MATCH ({sv}){arrow}{{1,{d}}}({name}:Sentence)
    """

    @property
    def collect(self) -> str:
        """uuid集計."""
        name = self.name
        return f"""
            , COLLECT(DISTINCT {name}.uid) AS {name}s
    """


class AdjType(Enum):
    """隣接タイプ."""

    PREMISE = ("premise", True, EdgeType.TO)
    CONCLUSION = ("conclusion", False, EdgeType.TO)
    REFRERD = ("referred", True, EdgeType.RESOLVED)
    REFER = ("refer", False, EdgeType.RESOLVED)
    ABSTRACT = ("abstract", True, EdgeType.EXAMPLE)
    EXAMPLE = ("example", False, EdgeType.EXAMPLE)

    def to_query(self, sent_var: str, dist: int | None) -> AdjQuery:
        """クエリ作成Classに変換."""
        return AdjQuery(
            sent_var=sent_var,
            reverse=self.value[1],
            name=self.value[0],
            dist=dist,
            et=self.value[2].name,
        )

    def match(self, sent_var: str, dist: int | None) -> str:
        """Match query."""
        if self == AdjType.EXAMPLE:
            return detail_match(sent_var, dist)
        name, rev, et = self.value
        ar = q_arrow(et.name, rev)
        d = "" if dist is None else str(dist)
        return f"""
        OPTIONAL MATCH ({sent_var}){ar}{{1,{d}}}({name}:Sentence)
    """

    @property
    def collect(self) -> str:
        """uuid集計."""
        name = self.value[0]
        return f"""
            , COLLECT(DISTINCT {name}.uid) AS {name}s
        """
