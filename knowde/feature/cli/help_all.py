"""help 詳細番."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import click
from sortedcontainers import SortedDict

if TYPE_CHECKING:
    from click.decorators import FC


def _add_format(
    ctx: click.Context,
    fmt: click.HelpFormatter,
    cmd: click.Command,
    sec_name: str,
) -> None:
    """formatにcmdのヘルプを追記."""
    opts = []
    for param in cmd.get_params(ctx):
        rv = param.get_help_record(ctx)
        if rv is not None:
            opts.append(rv)

    if opts:
        with fmt.section(sec_name):
            fmt.write_dl(opts)


def _add_format_recursive(
    ctx: click.Context,
    fmt: click.HelpFormatter,
    cmd: click.Command | click.Group,
) -> None:
    help_str = cmd.get_short_help_str()
    name = cmd.name
    _add_format(ctx, fmt, cmd, f"{name}  {help_str}")
    if isinstance(cmd, click.Group):
        with fmt.indentation():
            for subcmd in SortedDict(getattr(cmd, "commands", {})).values():
                _add_format_recursive(ctx, fmt, subcmd)


def help_all_callback(ctx: click.Context, _param: click.Parameter, _value: str) -> None:
    """Group Commandを展開して表示."""
    fmt = ctx.make_formatter()
    ctx.command.format_usage(ctx, fmt)
    ctx.command.format_help_text(ctx, fmt)

    _add_format(ctx, fmt, ctx.command, "RootOptions")
    commands = SortedDict(getattr(ctx.command, "commands", {}))
    with fmt.section("Commands"):
        for cmd in commands.values():
            _add_format_recursive(ctx, fmt, cmd)
    click.echo(fmt.getvalue().rstrip("\n"))
    ctx.exit()


def help_all_option() -> Callable[[FC], FC]:
    """コマンドを再帰的に全て表示."""
    return click.option(
        "--help-all",
        is_flag=True,
        callback=help_all_callback,
        help="再帰的にコマンド一覧を表示",
    )
