"""DBの読み取り."""

from __future__ import annotations

import click


@click.group("q")
def q_cli():
    """DBの読み取り."""


@q_cli.command("knowde")
def query_knowde():
    """DBの読み取り."""
