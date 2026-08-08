"""共通DBクエリ関連."""

from pydantic import BaseModel, Field


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

    @property
    def params(self) -> dict[str, int]:
        """cypher引数."""
        return {"offset": self.skip, "limit": self.size}

    @staticmethod
    def return_stmt(var: str) -> str:
        """ページのRETURN文."""
        return f"""
            RETURN
                SIZE({var}) AS total
                , {var}[$offset..$offset + $limit] AS page
        """


def q_call_term_names(var: str) -> str:
    """単文に定義された用語名を取得するCypher断片."""
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
