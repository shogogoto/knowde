"""for unit test."""
from knowde.feature.definition.domain.domain import DefinitionParam
from knowde.feature.definition.repo.definition import add_definition
from knowde.feature.definition.repo.statistics import find_statistics


def _p(name: str, explain: str) -> DefinitionParam:
    return DefinitionParam(name=name, explain=explain)


def test_isolate_stats() -> None:
    """孤立した定義."""
    d = add_definition(_p("p1", "s1"))
    stat = find_statistics(d.valid_uid)
    assert stat.nums == (0, 0, 0, 0)


def test_1src() -> None:
    """依存元srcが1つ."""
    d1 = add_definition(_p("p1", "s1"))
    d2 = add_definition(_p("p2", "s2-{p1}"))
    stat1 = find_statistics(d1.valid_uid)
    assert stat1.nums == (1, 0, 1, 0)
    stat2 = find_statistics(d2.valid_uid)
    assert stat2.nums == (0, 1, 0, 1)
