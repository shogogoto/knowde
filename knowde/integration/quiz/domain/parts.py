"""構成要素となる部品."""

from collections.abc import Hashable, Sequence
from enum import StrEnum
from functools import cache
from itertools import islice
from typing import Any, Final, Self

import networkx as nx
from more_itertools import pairwise
from pydantic import BaseModel

from knowde.feature.parsing.primitive.mark import inject2placeholder
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.shared.nxutil.edge_type import EdgeType

QUIZ_PLACEHOLDER = "$@"


class QuizStatementType(StrEnum):
    """問題文の種類."""

    SENT2TERM = "$@に合う用語を当ててください"
    TERM2SENT = "$@に合う文を当ててください"

    # 提示したEdgeTypeと関連する単文 or 定義を答えさせる
    EDGE2SENT = "$@と$@関係で繋がる単文を当ててください"
    # 提示した単文と対象間のEdgeTypeを答えさせる
    SENT2EDGE = "$@から$@への関係を当ててください"
    PATH = "$@の経路を当ててください"

    def inject(self, vals: list[str]) -> str:
        """プレースホルダーを置き換えて返す."""
        return inject2placeholder(
            str(self),
            vals,
            QUIZ_PLACEHOLDER,
            surround_pre="'",
            surround_post="'",
        )


def path2edgetypes(
    g: nx.DiGraph,
    s: Hashable,
    e: Hashable,
) -> tuple[list[EdgeType], bool]:
    """クイズ関係タイプへ変換."""
    try:
        # 正順
        p = nx.shortest_path(g, source=s, target=e)
        is_forward = True
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        # 逆順
        p = nx.shortest_path(g, source=e, target=s)
        is_forward = False
    ets = [EdgeType.get_edgetype(g, u, v) for u, v in pairwise(p)]
    # 単一要素のリストの場合に方向の判別がつかなくなるからis_forwardを返す
    return ets, is_forward


_REL_MAP: Final = [
    # type, backward, forward
    (EdgeType.BELOW, "PARENT", "DETAIL"),
    (EdgeType.TO, "PREMISE", "CONCLUSION"),
    (EdgeType.EXAMPLE, "GENERAL", "EXAMPLE"),
    (EdgeType.RESOLVED, "REF_BY", "REF"),
]


class QuizRel(StrEnum):
    """クイズ対象との関係."""

    PARENT = "親"
    DETAIL = "詳細"  # belowとその兄弟
    PREMISE = "前提"
    CONCLUSION = "結論"
    # 分かりにくい表現
    REFER = "用語参照"  # targetが参照する、根, source側
    REFERRED = "用語被参照"  # targetが参照される、葉, destination側
    GENERAL = "一般"
    EXAMPLE = "具体例"

    @classmethod
    @cache
    def forwards(cls) -> dict:
        """正順辞書."""
        return {
            EdgeType.TO: cls.CONCLUSION,
            EdgeType.RESOLVED: cls.REFERRED,
            EdgeType.EXAMPLE: cls.EXAMPLE,
            cls.DETAIL: cls.DETAIL,
        }

    @classmethod
    @cache
    def backwards(cls) -> dict:
        """正順辞書."""
        return {
            EdgeType.TO: cls.PREMISE,
            EdgeType.RESOLVED: cls.REFER,
            EdgeType.EXAMPLE: cls.GENERAL,
            cls.DETAIL: cls.PARENT,
        }

    @classmethod
    def of(
        cls,
        edge_types: Sequence[EdgeType],
        is_forward: bool,  # noqa: FBT001
    ) -> list[Self]:
        """クイズ関係タイプへ変換."""
        ets = to_detail_rel(edge_types)
        if is_forward:
            retval = [cls.forwards()[et] for et in ets]
        else:
            retval = reversed([cls.backwards()[et] for et in ets])
        return list(retval)


def count_consecutive_val(seq: Sequence, i_start: int, val: Any):
    """特定要素の連続回数を数える."""
    if i_start >= len(seq):
        return 0
    count = 0
    # start_index以降の要素を1つずつ取り出す
    for item in islice(seq, i_start, None):
        if item == val:
            count += 1
        else:
            break
    return count


def to_detail_rel(ets: Sequence[EdgeType | QuizRel]) -> Sequence[EdgeType | QuizRel]:
    """詳細関係への変換."""
    if EdgeType.BELOW not in ets:
        return ets
    i = ets.index(EdgeType.BELOW)
    retval = list(ets)
    try:
        n = count_consecutive_val(retval, i + 1, EdgeType.SIBLING)
        retval[i : i + n + 1] = [QuizRel.DETAIL]
    except IndexError:  # [BELOW]
        return [QuizRel.DETAIL]
    return to_detail_rel(retval)


# BELOW SIBLING * => DETAIL
# TO is_forward => CONCLUSION
# TO is_backward => PREMISE


# EdgeTypeとの重複あり
#   問題文への表示を司る
#   NwN1Labelと被ってる


class QuizOption(BaseModel, frozen=True):
    """クイズ選択肢."""

    val: str | Def | Hashable
    rel: QuizRel | None = None

    @classmethod
    def create(  # noqa: D102
        cls,
        sentence: str,
        names: list[str] | None = None,
        rel: QuizRel | None = None,
    ):
        val = Def.create(sentence, names=names)
        return cls(val=val, rel=rel)
