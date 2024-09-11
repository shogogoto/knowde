"""CLI test."""


from pathlib import Path

from click.testing import CliRunner

from knowde.feature.parser.domain.parser import transparse
from knowde.feature.parser.domain.transformer import common_transformer
from knowde.feature.parser.interface import parse_cmd

# source -> 論理行
#


def test_read() -> None:
    """Read text."""
    runner = CliRunner()
    p = Path(__file__).parent / "./sample/memo.md"
    result = runner.invoke(parse_cmd, [str(p)])
    _o = result.output

    _t = transparse(_o, common_transformer())
    # print(result.output)
    # print(_t)
    # print(_t.pretty())
