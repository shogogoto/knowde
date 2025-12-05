"""test title parse."""

from knowde.feature.parsing.title_parse import title_parse


def test_title_parse():
    """Title parse."""
    assert title_parse("# title") == "# title"

    assert (
        title_parse(
            """


        # title1
    """,
        )
        == "# title1"
    )

    assert (
        title_parse(
            """
        # title2
            aaaa
            xxx
            yyy
    """,
        )
        == "# title2"
    )
