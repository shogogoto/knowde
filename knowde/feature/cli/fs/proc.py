"""CLI用手続き."""


from pathlib import Path

import click

from knowde.complex.__core__.tree2net import parse2net
from knowde.primitive.config import LocalConfig


def link_proc() -> None:
    """DBと同期するファイルパスを指定."""
    current = Path.cwd()
    c = LocalConfig.load()
    c.ANCHOR = current
    c.save()
    click.echo(f"'{current}'をDBリンクとして設定しました")


class LinkNotExistsError(Exception):
    """リンク設定してない."""


def can_parse(s: str, show_error: bool) -> bool:  # noqa: FBT001
    """エラーなくパースできるか."""
    try:
        parse2net(s)
    except Exception as e:  # noqa: BLE001
        if show_error:
            print("    ", e)  # noqa: T201
        return False
    return True


def sync_proc(glob: str, show_error: bool = True) -> None:  # noqa: FBT001 FBT002
    """ファイルシステムと同期.

    ログイン(認証&user_id特定可能)
    anchorの設定 (そのpathの配下とDBPathがリンク)
    find 配下から再帰的にファイルパスリストを取得
    request data を作成
        parse check
            ng: continue
            ok:
                folder: folder名
                file: title, authors, published, url
        move前後を同定

    user_idからnamespaceを取得してそれとの差分を確認
        current にあってnsにない場合
            upload
        current になくてnsにある場合
            download
                git で管理してもらう前提だから不要
                -> だったら、syncではなくupload のが良い名前かも

    """
    c = LocalConfig.load()
    if c.ANCHOR is None:
        click.echo("同期するディレクトリをlinkコマンドで設定してください")
        return
    # fs = {}
    for p in c.ANCHOR.rglob(glob):
        rp = p.relative_to(c.ANCHOR)
        s = p.read_text()
        if not can_parse(s, show_error):
            click.echo(f"{rp}のパースに失敗しました")
            continue
    #     sn = parse2net(s)
    #     print(sn.root)
    #     st = p.stat().st_mtime  # 最終更新日時
    #     t = datetime.fromtimestamp(st, tz=TZ)
    #     # txt_hash = hash(s)  # ファイルに変更があったかをhash値で判断
    #     # print(t)
