"""リソース所有者判定."""

from neomodel.async_.core import AsyncDatabase

from knowde.shared.types import UUIDy, to_uuid


async def is_entry_owner(user_uid: UUIDy, entry_uid: UUIDy) -> bool:
    """エントリー所有者判定."""
    q = """
    RETURN EXISTS {
        MATCH (e:Entry {uid: $eid})
            -[:OWNED|PARENT]->*(u:User {uid: $uid})
    }
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={
            "eid": to_uuid(entry_uid).hex,
            "uid": to_uuid(user_uid).hex,
        },
    )
    return rows[0][0]
