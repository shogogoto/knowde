from __future__ import annotations

from inspect import signature
from uuid import UUID, uuid4

import click
import pytest
from click.testing import CliRunner

from .domain import VariadicArgumentsUndefinedError, each_args, rename_argument

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


def test_rename_argument() -> None:
    """Valid case."""

    def func(
        a: str,
        b: int,
        *args,  # noqa: ARG001, ANN002
        **kwargs,  # noqa: ARG001, ANN003
    ) -> tuple[str, int]:
        return a, b

    func2 = rename_argument("a", "replaced")(func)
    arg1, arg2 = "xyz", 1
    assert "replaced" not in str(signature(func))
    assert func(arg1, arg2) == func2(arg1, arg2)
    assert "replaced" in str(signature(func2))


def test_invalid_rename_argument() -> None:
    """Invalid case."""
    with pytest.raises(VariadicArgumentsUndefinedError):

        @rename_argument("a", "replaced")
        def func(a: str, b: int) -> tuple[str, int]:
            # def func(a: str, b: int) -> tuple[str, int]:
            return a, b
