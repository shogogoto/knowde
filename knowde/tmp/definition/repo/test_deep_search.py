"""文章にマークされた用語の定義をさらに遡ってマークを辿る."""

from knowde.tmp.definition.domain.domain import DefinitionParam
from knowde.tmp.definition.repo.deep_search import find_recursively
from knowde.tmp.definition.repo.definition import add_definition


def _p(name: str, explain: str) -> DefinitionParam:
    return DefinitionParam(name=name, explain=explain)


def test_resolve_marks_lv4() -> None:
    """文章にマークされた用語の定義をさらに遡ってマークを辿る.

    入力(s1:Sentence)から(t2:Term)を出力する
    (t1)-[:DEFINE]->(s1)-[:MARK]->(t2)
      -[:DEFINE]->(s2)-[:MARK]->(t3)->[:DEFINE]->(s3)


    同じtermが繰り返されるケース
    依存定義が繰り返し現れる場合、その表示を省略したい
    """
    d3 = add_definition("t3", "xxx")
    d21 = add_definition("t21", "xx{t3}xx")
    d22 = add_definition("t22", "xxxx")
    d1 = add_definition("t1", "xx{t21}xx{t22}")

    res = find_recursively(d1.valid_uid)
    assert res.rootdef == d1
    assert res.get_children(d1) == [d21, d22]
    assert res.get_children(d21) == [d3]
    assert res.get_children(d22) == []
    assert res.get_children(d3) == []
