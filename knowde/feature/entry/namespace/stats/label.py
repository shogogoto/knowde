"""リソース統計情報のneo4j label."""

from neomodel import AsyncStructuredNode, IntegerProperty


class LResourceStatsCache(AsyncStructuredNode):
    """リソースの統計情報."""

    __label__ = "ResourceStatsCache"
    n_sentence = IntegerProperty()
    n_term = IntegerProperty()
    n_char = IntegerProperty()
    n_edge = IntegerProperty()
    n_isolation = IntegerProperty()

    # グラフ理論の指標 計算重いかも
    # やるなら neo4jではなく networkx でまず作るか
    #   <- CLIでも使えるから
