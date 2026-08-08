"""クイズ関係タイプテスト."""

from knowde.shared.nxutil.edge_type import EdgeType

from .rel import QUIZ_REL_EDGE_TYPES, QuizRel, edgetype2rel


def test_quiz_rel_edge_types():
    """クイズとして表示できる関係だけをpath探索に使う."""
    assert EdgeType.TO in QUIZ_REL_EDGE_TYPES
    assert EdgeType.BY not in QUIZ_REL_EDGE_TYPES


def test_referred_label():
    """被参照関係は冗長な「用語」を付けずに表示する."""
    assert QuizRel.REFERRED == "被参照"


def test_to_detail_rel():
    """親子関係変換."""
    # 変換しない
    assert edgetype2rel([]) == []
    assert edgetype2rel([EdgeType.SIBLING]) == [QuizRel.PEER]
    assert edgetype2rel([EdgeType.SIBLING] * 3) == [QuizRel.PEER]
    assert edgetype2rel([EdgeType.TO]) == [EdgeType.TO]

    # 複数兄弟を含めて1つに変換
    assert edgetype2rel([EdgeType.BELOW]) == [QuizRel.DETAIL]
    one = [EdgeType.BELOW, *[EdgeType.SIBLING] * 3]
    assert edgetype2rel(one) == [QuizRel.DETAIL]

    # 2つあれば2つに
    assert edgetype2rel([*one, *one]) == [QuizRel.DETAIL] * 2

    # 混じってる
    assert edgetype2rel([*one, EdgeType.TO, *one]) == [
        QuizRel.DETAIL,
        EdgeType.TO,
        QuizRel.DETAIL,
    ]


def test_edgetypes2rel():
    """関係リストからクイズ関係を得る."""
    one = [EdgeType.BELOW, *[EdgeType.SIBLING] * 3]
    # detail
    assert QuizRel.of([EdgeType.BELOW], True) == [QuizRel.DETAIL]  # noqa: FBT003
    assert QuizRel.of(one * 2, True) == [QuizRel.DETAIL, QuizRel.DETAIL]  # noqa: FBT003
    assert QuizRel.of([EdgeType.BELOW], False) == [QuizRel.PARENT]  # noqa: FBT003
    assert QuizRel.of(one * 2, False) == [QuizRel.PARENT] * 2  # noqa: FBT003
    # to
    assert QuizRel.of([EdgeType.TO, EdgeType.TO], True) == [QuizRel.CONCLUSION] * 2  # noqa: FBT003
    assert QuizRel.of([EdgeType.TO, EdgeType.TO], False) == [QuizRel.PREMISE] * 2  # noqa: FBT003
    # 混在
    assert QuizRel.of([*one, EdgeType.TO, *one], True) == [  # noqa: FBT003
        # detail to detail
        QuizRel.DETAIL,
        QuizRel.CONCLUSION,
        QuizRel.DETAIL,
    ]
    # 複雑なパターンは網羅できてなさそうだが、そんなクイズ要るか?
    # 一旦ペンディング
