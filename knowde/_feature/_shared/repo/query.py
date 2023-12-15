from __future__ import annotations

from textwrap import dedent
from typing import Any, Optional

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
    return QueryResult(results=results, meta=meta)


class QueryResult(BaseModel, frozen=True):
    results: list[list[Any]]
    meta: list[str]

    def get(self, retvar: str) -> list[Any]:
        i = self.meta.index(retvar)
        cols = [row[i] for row in self.results]
        return list(filter(lambda x: x is not None, cols))
