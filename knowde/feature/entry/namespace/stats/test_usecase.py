"""test usecase."""

from knowde.feature.entry.namespace.stats.usecase import to_resource_stats


def test_echo_resource_stats():
    """Aaaa."""
    txt = """
        # title1
            @author John Due
        ## xxx
            x
            y
            z
              -> w
    """

    stats = to_resource_stats(txt, False)  # noqa: FBT003
    assert stats == {
        "n_char": 26,
        "n_sentence": 4,
        "n_term": 0,
        "n_edges": 6,
        "n_isolation": 2,
        "n_axiom": 1,
        "n_unrefered": 0,
        "r_isolation": 0.5,
        "r_axiom": 0.25,
        "r_unrefered": 0.0,
    }

    stats = to_resource_stats(txt, True)  # noqa: FBT003

    assert stats == {
        "n_char": 26,
        "n_sentence": 4,
        "n_term": 0,
        "n_edges": 6,
        "n_isolation": 2,
        "n_axiom": 1,
        "n_unrefered": 0,
        "r_isolation": 0.5,
        "r_axiom": 0.25,
        "r_unrefered": 0.0,
        "density": 0.14285714285714285,
    }
