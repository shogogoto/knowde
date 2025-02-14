"""auth cli."""

import click


@click.command("login")
def login_cmd() -> None:
    """Login."""
    from .proc import browse_for_sso

    _user = browse_for_sso()


@click.command("signup")
@click.argument("email", type=click.STRING)
@click.password_option()
def signup_cmd(email: str, password: str) -> None:
    """アカウント作成."""
    from .proc import sign_up_proc

    sign_up_proc()
    click.echo(f"{email}:{password}")
