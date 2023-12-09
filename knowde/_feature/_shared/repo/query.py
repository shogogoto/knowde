from __future__ import annotations

from textwrap import dedent
from typing import Any, Optional

from neomodel import db


def query_cypher(
    query: str,
    params: Optional[dict[str, Any]] = None,
    handle_unique: bool = True,  # noqa: FBT001 FBT002
    retry_on_session_expire: bool = False,  # noqa: FBT001 FBT002
    resolve_objects: bool = True,  # noqa: FBT001 FBT002
) -> tuple[list[Any], list[str]]:
    """cypher_query wrapped."""
    _q = dedent(query).strip()
    results, meta = db.cypher_query(
        _q,
        params=params,
        handle_unique=handle_unique,
        retry_on_session_expire=retry_on_session_expire,
        resolve_objects=resolve_objects,
    )
    return results, meta
