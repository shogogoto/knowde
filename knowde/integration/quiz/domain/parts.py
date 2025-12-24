"""構成要素となる部品."""

from collections.abc import Hashable, Sequence
from enum import StrEnum
from functools import cache
from itertools import islice
from typing import Any, Self

import networkx as nx
from more_itertools import pairwise
from pydantic import BaseModel

from knowde.feature.parsing.primitive.mark import inject2placeholder
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.shared.nxutil.edge_type import EdgeType

QUIZ_PLACEHOLDER = "$@"


class QuizType(StrEnum):
    """問題文の種類."""

    SENT2TERM = "$@に合う用語を当ててください"
    TERM2SENT = "$@に合う文を当ててください"

    # 提示したEdgeTypeと関連する単文 or 定義を答えさせる
    REL2SENT = "$@と$@関係で繋がる単文を当ててください"
    # 提示した単文と対象間のEdgeTypeを答えさせる
    SENT2REL = "$@から$@への関係を当ててください"
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
    # to, to が premise * 2 か conclusion * 2 か判別できるように is_forward を返す
    return ets, is_forward


class QuizRel(StrEnum):
    """クイズ対象との関係."""

    PARENT = "親"
    DETAIL = "詳細"  # belowとその兄弟
    PEER = "同階層"

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
            cls.PEER: cls.PEER,
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
            cls.PEER: cls.PEER,
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
    retval = list(ets)
    if EdgeType.BELOW not in ets:
        if EdgeType.SIBLING in ets:
            i = ets.index(EdgeType.SIBLING)
            n = count_consecutive_val(ets, i, EdgeType.SIBLING)
            retval[i : i + n + 1] = [QuizRel.PEER]
            return to_detail_rel(retval)

        return ets
    i = ets.index(EdgeType.BELOW)

    try:
        n = count_consecutive_val(retval, i + 1, EdgeType.SIBLING)
        retval[i : i + n + 1] = [QuizRel.DETAIL]
    except IndexError:  # [BELOW]
        return [QuizRel.DETAIL]
    return to_detail_rel(retval)


class QuizOption(BaseModel, frozen=True):
    """クイズ選択肢."""

    val: str | Def | Hashable
    rels: Sequence[QuizRel] | None = None

    @classmethod
    def create(  # noqa: D102
        cls,
        sentence: str,
        names: list[str] | None = None,
        rel: QuizRel | None = None,
    ):
        val = Def.create(sentence, names=names)
        return cls(val=val, rel=rel)

    @property
    def rels_stmt(self) -> str:
        """選択肢の関係の文言."""
        if self.rels is None:
            msg = "rel is None"
            raise ValueError(msg)
        return "の".join([str(r) for r in self.rels])

    @property
    def sentence(self) -> str:
        """単文表現."""
        if isinstance(self.val, Def):
            return str(self.val.sentence)
        return str(self.val)
