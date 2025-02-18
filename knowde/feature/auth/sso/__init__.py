"""single sign on."""
from __future__ import annotations

import json
import webbrowser

import click
import httpx

from knowde.feature.auth.cli.proc import auth_file
from knowde.feature.auth.sso.route import (
    GOOGLE_URL,
)


def browse_for_sso() -> None:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = 8000

    url = f"http://localhost:{port}{GOOGLE_URL}/authorize"
    client = httpx.Client()
    res = client.get(url)
    auth_url = res.json().get("authorization_url")
    webbrowser.open(auth_url)
    click.echo(
        '{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNWQ3NWViZi1mZmRlLTQ3OTQtYmFhYy0xY2VjYTc1NzFmYmEiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTczOTk1NzQ4NH0.YoEk4jsjKbHx041JHyweHcYIIDocK0x0K8qwbtbWD4Y","token_type":"bearer"}',
    )
    res_text = input("認証後ブラウザに上記のようなレスポンスを入力してください:")
    p = auth_file()
    js = json.loads(res_text)
    js = json.dumps(js, indent=2)
    p.write_text(js)
    click.echo(f"{p}を以下で上書きしました")
    click.echo(js)
