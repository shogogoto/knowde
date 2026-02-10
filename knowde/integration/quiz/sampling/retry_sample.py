"""候補から選択肢を選ぶ."""


# # 詳細や結論などの特定の関係内から探す
# # scoreでソートできたほうが良い
# async def list_candidates_by_rel_type(target_sent_id: UUIDy):
#     pass


# 引数をbindした関数
# その内の１つのパラメータを指定し、それを+1してリトライ
# async def retry_sample_incr(
#     target_sent_uid: UUIDy,
#     radius: int,
#     n_option: int,  # 選択肢の数
#     n_retry: int = 5,  # 失敗時に半径をインクリして繰り返す回数
#     has_term: bool = False,
# ) -> list[UUID]:
#     """条件を緩めながら一定の候補数になるまで取得を試す."""
#     r = radius
#     last_n_cand = -1  # 0以上だと初回でループが終了してしまう可能性
#     attempt = 0
#     for attempt in range(1, n_retry + 1):
#         cand_uids = await list_candidates_by_radius(
#             target_sent_uid,
#             r,
#             has_term,
#         )
#         current_n_cand = len(cand_uids)
#         # 半径を増やしても候補が増えないならretryしても無駄
#         if last_n_cand == current_n_cand:
#             break
#         last_n_cand = len(cand_uids)
#         try:
#             return sample_safe(cand_uids, n_option=n_option)
#         except SamplingError:
#             r += 1
#             continue
#     msg = (
#         f"指定数だけの選択肢を取得できなかった: "
#         f"試行回数={attempt}/{n_retry}"
#         f", 最終半径={radius}->{r}"
#         f", 最終候補数={last_n_cand}"
#     )
#     raise SamplingError(msg)
