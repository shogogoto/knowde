"""シェル補間."""
import os
from pathlib import Path
from typing import Callable, Final

import click
from click.decorators import FC

VAR: Final = "_KN_COMPLETE"

C_CONF: Final = {
    "bash": (f'eval "$({VAR}=bash_source kn)"', ".bashrc"),
    "zsh": (f'eval "$({VAR}=zsh_source kn)"', ".zshrc"),
    "fish": (f"{VAR}=fish_source kn | source", ".config/fish/config.fish"),
}


def completion_callback(
    ctx: click.Context,
    _param: click.Parameter,
    value: str,
) -> None:
    """シェルタイプを判定して補完設定を行うコールバック関数."""
    if not value or ctx.resilient_parsing:
        return
    shell = value or os.environ.get("SHELL", "")
    shells = [sh for sh in C_CONF if sh in shell]
    if len(shells) == 0:
        click.Abort("補完機能に対応しないシェルです", shell)
    script, rc_name = C_CONF[shells[0]]

    rc = Path.home() / rc_name
    rc.parent.mkdir(parents=True, exist_ok=True)
    if rc.exists() and script in rc.read_text():
        click.echo("Already setup knowde completion.")
        ctx.exit()

    with Path.open(rc, "a") as f:
        f.write(f"{script} # knowde completion setting\n")
    click.echo(f"Completion setup for {shell} completed!")
    click.echo(f"Please restart your shell or run: source {rc}")
    ctx.exit()


def complete_option() -> Callable[[FC], FC]:
    """CLI補完."""
    return click.option(
        "--shell",
        type=click.Choice(list(C_CONF.keys())),
        expose_value=False,
        is_eager=True,
        callback=completion_callback,
        flag_value="bash",
        help="CLI補完設定を.bashrcなどに追記する.",
    )
