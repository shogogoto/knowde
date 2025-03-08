"""CLI用手続き."""


from pathlib import Path

import click

from knowde.complex.auth.repo.client import auth_header
from knowde.complex.resource.router import SyncFilesData
from knowde.feature.cli.fs.sync import can_parse, read_meta
from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import Settings


def link_proc() -> None:
    """DBと同期するファイルパスを指定."""
    current = Path.cwd()
    c = LocalConfig.load()
    c.ANCHOR = current
    c.save()
    click.echo(f"'{current}'をDBリンクとして設定しました")


class LinkNotExistsError(Exception):
    """リンク設定してない."""


def sync_proc(glob: str, show_error: bool = True) -> None:  # noqa: FBT001 FBT002
    """ファイルシステムと同期.

    ログイン(認証&user_id特定可能)
    anchorの設定 (そのpathの配下とDBPathがリンク)
    anchor配下から再帰的にファイルパスリストを取得
    request data を作成
        parse check
            ng: continue
            ok:
                folder: folder名
                file: title, authors, published, url
    差分変更箇所チェック api へ送る
        req 内容をそれぞれ判定
            reqとdb のentryを対応づける
                変更あり/なし テキストhashの変更あり/なし
                削除
                新規
                (移動) move前後を同定
                    削除 と 新規 のリスト
                      ファイル名の変更は影響しない なぜなら # title が entry名.
        {"req path": {
            "db_path": ~,
            ""
        }}

        response アップロードすべきファイルを指示

    batch_upload api
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
    headers = auth_header()  # ユーザーを待たせないためにparse前に失敗したい
    data = SyncFilesData(root=[])
    for p in c.ANCHOR.rglob(glob):
        if not can_parse(p, show_error):
            continue
        meta = read_meta(p)
        meta.path = p.relative_to(c.ANCHOR).parts
        data.root.append(meta)
    s = Settings()
    _res = s.post("namespace", json=data.model_dump(mode="json"), headers=headers)
