"""遅延importでCLI補間軽くするための分離."""
from __future__ import annotations

import json
import webbrowser

import click
import requests

from knowde.primitive.config import LocalConfig


def browse_for_sso() -> bool:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = 8000

    url = f"http://localhost:{port}/google/authorize"
    try:
        res = requests.get(url, timeout=3)
    except requests.ConnectionError:
        click.echo(f"認証URL'{url}'への接続に失敗しました")
        return False
    auth_url = res.json().get("authorization_url")
    webbrowser.open(auth_url)
    click.echo(
        '{"access_token":"eyJh...","token_type":"bearer"}',
    )
    res_text = input("認証後ブラウザに上記のようなレスポンスを入力してください:")
    c = LocalConfig.load()
    c.CREDENTIALS = json.loads(res_text)
    c.save()
    click.echo("認証情報を保存しました")
    click.echo(c.CREDENTIALS)
    return True
