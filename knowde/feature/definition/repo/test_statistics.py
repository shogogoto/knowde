"""for unit test."""
from knowde.feature.definition.domain.domain import DefinitionParam


def _p(name: str, explain: str) -> DefinitionParam:
    return DefinitionParam(name=name, explain=explain)


def test_get_isolate_stats() -> None:
    """依存情報の取得."""
    # add_definition(_p("p1", ""))
    # d = add_definition(_p("p2", "{p1}"))
    # print("##########")
    # print(view_detail(find_recursively(d.valid_uid).build()))
