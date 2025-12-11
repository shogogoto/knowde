"""誤答肢.

>>誤答肢は、受験者たちの一般的な誤解やよくある間違いに基づくもので、
>>正解の選択肢と混同しやすいなど合理的に誤解され得る内容でなければなりません.

正解は簡単に決まる
誤答を上手く選ぶことがクイズ機能の主
DBから直接探すのがいい sysnetを復元するのは非効率

誤答肢を見て、これ何だろう、と思ったらクイズチェーンでそこからクイズを
作っていける
"""

from uuid import UUID

from neomodel import adb

from knowde.shared.types import UUIDy, to_uuid


async def list_distractor_candidates(
    target_sent_id: UUIDy,
    dist: int | None = None,  # 探索半径
    has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """誤答肢候補の単文uidを列挙する.

    詳細や結論などの特定の関係内から探す
    """
    q_term = "<-[:DEF]-(:Term)" if has_term else ""
    if dist is None:
        q = f"""
        MATCH (sent:Sentence {{uid: $sent_uid}})
        OPTIONAL MATCH (s:Sentence {{resource_uid: sent.resource_uid}})
            {q_term}
        WHERE s.uid <> sent.uid
        RETURN sent.uid
        """
    else:
        if dist <= 0:
            msg = "dist must be > 0"
            raise ValueError(msg)
        q = f"""
            MATCH (sent:Sentence {{uid: $sent_uid}})
            // dist=1.. にすることで sent_uidを含めない
            OPTIONAL MATCH (sent)-[]-{{1, {dist}}}(e:Sentence)
                {q_term}
            RETURN e.uid
        """

    rows, _ = await adb.cypher_query(
        q,
        params={"sent_uid": to_uuid(target_sent_id).hex},
    )
    return [to_uuid(row[0]) for row in rows]


async def choose_distractor():
    """誤答肢を候補から選ぶ."""
