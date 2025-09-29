"""句."""

from enum import StrEnum

from pydantic import BaseModel, Field


class WherePhrase(StrEnum):
    """WHERE句の条件."""

    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS WITH"
    ENDS_WITH = "ENDS WITH"
    REGEX = "=~"
    EQUAL = "="


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
    """ORDER BY句."""

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
