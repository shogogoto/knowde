"""クエリの共通部分."""


def q_archivement(user_var: str) -> str:
    """成果の集計."""
    return f"""
        OPTIONAL MATCH ({user_var})<-[:OWNED|PARENT]-*(r:Resource)
            -[:STATS]->(stat:ResourceStatsCache)
        WITH {user_var}
            , SUM(stat.n_char) AS n_char
            , SUM(stat.n_sentence) AS n_sentence
            , COUNT(r) AS n_resource
    """
