from __future__ import annotations

from textwrap import dedent
from typing import Any, Callable, Optional

from neomodel import db
from pydantic import BaseModel


def query_cypher(
    query: str,
    params: Optional[dict[str, Any]] = None,
    handle_unique: bool = True,  # noqa: FBT001 FBT002
    retry_on_session_expire: bool = False,  # noqa: FBT001 FBT002
    resolve_objects: bool = True,  # noqa: FBT001 FBT002
) -> QueryResult:
    """cypher_query wrapped."""
    _q = dedent(query).strip()
    results, meta = db.cypher_query(
        _q,
        params=params,
        handle_unique=handle_unique,
        retry_on_session_expire=retry_on_session_expire,
        resolve_objects=resolve_objects,
    )
    return QueryResult(q=_q, results=results, meta=meta)


class QueryResult(BaseModel, frozen=True):
    q: str
    results: list[list[Any]]
    meta: list[str]

    def get(
        self,
        var: str,
        convert: Callable[[Any], Any] = lambda x: x,
        row_convert: Callable[[Any], Any] = lambda x: x,
    ) -> list[Any]:
        i = self.meta.index(var)
        return list(
            map(
                convert,
                [row_convert(row[i]) for row in self.results],  # None削除
            ),
        )

    def item(self, i: int, *vars_: str) -> list[Any]:
        idxs = [self.meta.index(var) for var in vars_]
        row = self.results[i]
        return [row[i] for i in idxs]

    def items(self, *vars_: str) -> list[list[Any]]:
        idxs = [self.meta.index(var) for var in vars_]
        return [[row[i] for i in idxs] for row in self.results]

    def tuple(self, *vars_: str) -> tuple[Any, ...]:
        return tuple([self.get(var) for var in vars_])
