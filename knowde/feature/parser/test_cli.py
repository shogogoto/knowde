"""CLI test."""


from pathlib import Path

from click.testing import CliRunner

from knowde.feature.parser.interface import parse_cmd

# source -> 論理行
#


def test_read() -> None:
    """Read text."""
    runner = CliRunner()
    p = Path(__file__).parent / "./sample/2アジャイルサムライ.md"
    result = runner.invoke(parse_cmd, [str(p)])
    _o = result.output
    # print(result.output)
