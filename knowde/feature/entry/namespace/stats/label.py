"""リソース統計情報のneo4j label."""

from neomodel import AsyncStructuredNode, FloatProperty, IntegerProperty


class LResourceStatsCache(AsyncStructuredNode):
    """リソースの統計情報."""

    __label__ = "ResourceStatsCache"
    n_char = IntegerProperty()
    n_sentence = IntegerProperty()
    n_term = IntegerProperty()
    n_edge = IntegerProperty()
    n_isolation = IntegerProperty()
    n_axiom = IntegerProperty()
    n_unrefered = IntegerProperty()

    # 計算可能 computed_field なものは記録しない
    # heavy
    # グラフ理論の指標 計算重いかも
    # やるなら neo4jではなく networkx でまず作るか
    #   <- CLIでも使えるから
    average_degree = FloatProperty()
    density = FloatProperty()
    diameter = FloatProperty()
    radius = FloatProperty()
    n_scc = IntegerProperty()
