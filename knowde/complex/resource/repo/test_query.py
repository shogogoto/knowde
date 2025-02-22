"""系の永続化.

Userそれぞれがsourceを持つ

User名一覧
    /users
    /users/prof userのプロフィール
        文の総数とか
        biograph

user -> folder -> resource
folderを噛ませることでtitleの重複回避を可能にしたい
いや、resource_idをUUIDにすればええやん
    userから直接 resourceと紐付ければよい

分類戦略 category
    フォルダ分け 階層
    Tag resourceのmeta dataとして扱う

resource
    title
    author
    published
    url
    TOC の生成

User機能
    follow/follower
    team
    share 共同編集権限
    guest shareな記事しか作れない

User配下の情報
User
> folder 再帰的構造
> resource_id(= 系の名前)
> heading
> sysnode

でシームレスにsysnode一覧を取得できる
indicator = /user/folder[/heading]

系の識別子 resource
初期フォルダーをデフォルトで作成
resource総数
define総数
活動履歴(追加データを最新順で表示)
path > resource名 統計値　一覧

CLI find して ファイルパスの構造をそのままsync(永続化)
  -> Git管理できて便利
"""



import pytest
from neomodel import db

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.resource.repo import sysnet2cypher
from knowde.complex.resource.repo.labels import LResource


@pytest.fixture()
def sn() -> SysNet:  # noqa: D103
    # b{A}b が自身にRESOLVED関係を持っていて謎
    _s = r"""
        # h1
            @author nanashi
            @author taro tanaka
            @published 1919
            A: df
            P1 |B: b{A}b
            C{B}: ccc
            D: d{CB}d
        ## h2
            P{D}: ppp
            Q: qqq
            c{A}c
            X:
        ### h31
        ### h32
    """
    return parse2net(_s)


def test_save_and_restore(sn: SysNet) -> None:
    """永続化して元に戻す."""
    q = sysnet2cypher(sn)
    db.cypher_query(q)
    assert LResource.nodes.get(title="# h1")
    # sleep(10000)
