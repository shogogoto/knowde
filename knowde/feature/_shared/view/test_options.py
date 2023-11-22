"""view test."""
from __future__ import annotations

import json

import click
from click.testing import CliRunner

from .options import view_options
from .test_domain import OneModel

models = [OneModel(p1=str(i), p2="xxx") for i in range(3)]


@click.command("test")
@click.argument("arg", nargs=1)
@click.option("--op", type=click.INT, default=None)
@view_options
def command(arg: str, op: int | None) -> list[OneModel]:  # noqa: ARG001
    """With dummy arg and option."""
    return models


def test_view_json() -> None:
    runner = CliRunner()
    result = runner.invoke(
        command,
        ["test", "--op", "111", "-S", "json"],
    )
    assert result.exit_code == 0
    assert json.loads(result.output) == [
        {"p1": "0", "p2": "xxx"},
        {"p1": "1", "p2": "xxx"},
        {"p1": "2", "p2": "xxx"},
    ]


def test_view_table() -> None:
    runner = CliRunner()
    result = runner.invoke(
        command,
        ["test", "--op", "111", "-P", "p1", "-S", "table"],
    )

    lines = [
        "      p1",
        "--  ----",
        " 0     0",
        " 1     1",
        " 2     2",
        "",
    ]
    expected = "\n".join(lines)
    assert result.exit_code == 0
    assert result.stdout == expected


def test_view_rows() -> None:
    runner = CliRunner()
    result = runner.invoke(
        command,
        ["test", "--op", "111", "-P", "p1", "-S", "rows"],
    )

    lines = [
        "0",
        "1",
        "2",
        "",
    ]
    expected = "\n".join(lines)
    assert result.exit_code == 0
    assert result.stdout == expected
