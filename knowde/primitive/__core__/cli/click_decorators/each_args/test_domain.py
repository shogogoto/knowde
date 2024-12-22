"""test."""
from __future__ import annotations

from uuid import UUID, uuid4

import click
from click.testing import CliRunner

from .domain import each_args

ONE = uuid4()


def complete(_: str) -> UUID:
    """Mock."""
    return ONE


@click.command()
@each_args(converter=complete)
def cli(uid: UUID) -> None:
    """Testee cli."""
    click.echo(f"{uid} was input")


@click.command()
@click.option("--option", "-o")
@each_args(converter=complete)
def cli_with_other_options(uid: UUID, option: str) -> None:
    """Testee cli2."""
    click.echo(f"{uid} and {option}")


def test_uuid_target_option() -> None:
    """uuid_target_optionsデコレータのテスト."""
    runner = CliRunner()
    uid = str(ONE)
    result = runner.invoke(cli, [str(uid)])
    assert uid in result.stdout


def test_with_other_option() -> None:
    """Another case."""
    runner = CliRunner()
    uid = str(ONE)
    result = runner.invoke(
        cli_with_other_options,
        [uid, "-o", "opt"],
    )
    assert uid in result.stdout
    assert "opt" in result.stdout
