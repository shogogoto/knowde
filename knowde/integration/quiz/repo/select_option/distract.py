"""誤答肢.

>>誤答肢は、受験者たちの一般的な誤解やよくある間違いに基づくもので、
>>正解の選択肢と混同しやすいなど合理的に誤解され得る内容でなければなりません.

正解は簡単に決まる
誤答を上手く選ぶことがクイズ機能の主
DBから直接探すのがいい sysnetを復元するのは非効率

誤答肢を見て、これ何だろう、と思ったらクイズチェーンでそこからクイズを
作っていける
"""

from collections.abc import Iterable
from typing import Annotated
from uuid import UUID

from neomodel import adb
from pydantic import Field, TypeAdapter

from knowde.shared.types import UUIDy, to_uuid


async def list_candidates_in_resource(
    target_sent_id: UUIDy,
    has_term: bool = False,  # noqa: FBT001, FBT002
):
    """リソース内全ての単文を選択肢候補として列挙."""
    q_term = "<-[:DEF]-(:Term)" if has_term else ""
    q = f"""
        MATCH (sent:Sentence {{uid: $sent_uid}})
        OPTIONAL MATCH (s:Sentence {{resource_uid: sent.resource_uid}})
            {q_term}
        WHERE s.uid <> sent.uid
        RETURN
            s.uid
    """
    uid = to_uuid(target_sent_id).hex
    rows, _ = await adb.cypher_query(q, params={"sent_uid": uid})
    return [row[0] for row in rows]


type Radius = Annotated[int, Field(gt=0, title="探索半径")]
r_adapter = TypeAdapter(Radius)


async def list_candidates_by_radius(
    target_sent_id: UUIDy,
    radius: Radius,
    has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """距離指定で選択肢候補を列挙."""
    radius = r_adapter.validate_python(radius)
    q_term = "<-[:DEF]-(:Term)" if has_term else ""
    q = f"""
        MATCH (sent:Sentence {{uid: $sent_uid}})
        // dist=1.. にすることで sent_uidを含めない
        OPTIONAL MATCH p = (sent)-[]-{{1, {radius}}}(e:Sentence)
            {q_term}
        RETURN e.uid
    """
    rows, _ = await adb.cypher_query(
        q,
        params={"sent_uid": to_uuid(target_sent_id).hex},
    )
    return [row[0] for row in rows]


# # 詳細や結論などの特定の関係内から探す
# # scoreでソートできたほうが良い
# async def list_candidates_by_rel_type(target_sent_id: UUIDy):
#     pass


# random
async def choose_distractor(cand_uuids: Iterable[UUIDy], n_choose: int):
    """誤答肢を候補から選ぶ.

    cand_uuids: 誤答肢候補のuidのリスト
    n_choose: 選ぶ数
    """
    # uids = [to_uuid(uid).hex for uid in cand_uuids]
    # kns = await fetch_knowdes_with_detail(uids)

    # print("*" * 100)
    # print(kns)
    # cand_uuidsから詳細を取得

    # その中から返すものを絞る
    # まずはランダムに3つ返すだけにするか
