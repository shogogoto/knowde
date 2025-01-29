"""シェル補間."""
import os
from pathlib import Path

import click


def completion_callback(
    ctx: click.Context,
    _param: click.Parameter,
    value: str,
) -> None:
    """シェルタイプを判定して補完設定を行うコールバック関数."""
    if not value or ctx.resilient_parsing:
        return
    shell = value or os.environ.get("SHELL", "")
    var = "_KN_COMPLETE"
    if "zsh" in shell:
        shell = "zsh"
    elif "fish" in shell:
        shell = "fish"
    elif "bash" in shell:
        shell = "bash"
    else:
        click.Abort("補完機能に対応しないシェルです", shell)

    script, rc_path = {
        "bash": (f'eval "$({var}=bash_source kn)"', ".bashrc"),
        "zsh": (f'eval "$({var}=zsh_source kn)"', ".zshrc"),
        "fish": (f"{var}=fish_source kn | source", ".config/fish/config.fish"),
    }[shell]

    script = f"{script} # knowde completion setting\n"
    rc_path = Path.home() / rc_path
    rc_path.parent.mkdir(parents=True, exist_ok=True)

    # 既存の設定チェック
    if rc_path.exists():
        content = rc_path.read_text()
        if script in content:
            click.echo("Already setup knowde completion.")
            ctx.exit()

    # 設定の書き込み
    with Path.open(rc_path, "a") as f:
        f.write(script)

    click.echo(f"Completion setup for {shell} completed!")
    click.echo(f"Please restart your shell or run: source {rc_path}")
    ctx.exit()
