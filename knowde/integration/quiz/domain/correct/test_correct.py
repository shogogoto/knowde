"""正答の指定ロジック."""

import uuid

import pytest

from knowde.feature.parsing.sysnet import SysNet
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizOption, QuizRel, QuizType
from knowde.integration.quiz.fixture import fx_sn

sn = pytest.fixture(fx_sn)


def test_correct_rel_by_id(sn: SysNet):
    """クイズ対象と指定選択肢間の関係を正答にする."""
    _src = QuizSource(
        quiz_id=uuid.uuid4().hex,
        statement_type=QuizType.REL2SENT,
        target_id="1",  # 問いの対象
        target=QuizOption(val=sn.get("ccc"), rels=[QuizRel.DETAIL]),
        sources={
            "2": QuizOption(val=sn.get("ccc1"), rels=[QuizRel.DETAIL]),
            "3": QuizOption(val=sn.get("to"), rels=[QuizRel.CONCLUSION]),
            "4": QuizOption(val=sn.get("cccb"), rels=[QuizRel.PREMISE]),
            "5": QuizOption(val=sn.get("cccb1"), rels=[QuizRel.PREMISE]),
            "6": QuizOption(val=sn.get("parent"), rels=[QuizRel.PARENT]),
        },
    )
    # print(src.get_by_id("3").rels)
    # f = correct_rels_by_id(src, "3")

    # assser[id_ for id_ in src.ids if f(id_)]

    # raise AssertionError
