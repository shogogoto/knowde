"""userに所有されたsysnet.

category
    フォルダ分け 階層
    タグ resourceのmeta dataとして扱う?

permission アクセス権限 MVPには不要
    Owner機能 SysNetの所有者
        <-> Guest機能
            read only
            guest配下の編集権限
        globalとの違いは?

    team userが所属 leader が user add remove などの権限

{user_id}/path/title/文
{user_id}/path/sentences
{user_id}/path/defs


User folderやsysnetの永続化のために要求される機能だけを考えろ
  Resource依存機能
    一覧 /users get user名やプロフィール一覧
    Profile
        戦闘力(Power) 文の総数とか
            resource総数
            define総数
        活動履歴(追加データを最新順で表示)
        biograph
    share 共同編集権限
        guest shareな記事しか作れない
        <=> folderの編集権限

    favorite

view
    path > resource名 統計値　一覧
    TOC 見出しツリー
    indicator 文の位置情報 パスみたいな単一文字列をイメージしてたが、dictにしよう
        folder path
            title前 userId / folder
        userId/folder/title(H1)/h2...h6/文
            title後 見出し // URLには含めないでおこう、長くなりすぎそう
        文脈
            below parent
            premise... など
"""
from __future__ import annotations

from datetime import date, datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, Field

from knowde.primitive.time import parse2dt

if TYPE_CHECKING:
    from knowde.complex.__core__.sysnet import SysNet


class ResourceMeta(BaseModel):
    """リソースメタ情報."""

    title: str
    authors: list[str] = Field(default_factory=list)
    published: date | None = None
    urls: list[str] = Field(default_factory=list)

    # ファイル由来
    path: tuple[str, ...] | None = Field(default=None, min_length=1)
    updated: datetime | None = None
    txt_hash: int | None = None

    @property
    def names(self) -> tuple[str, ...]:
        """文字列へ."""
        if self.path is None:
            return ()
        if len(self.path) == 0:
            return ()
        ret = list(self.path)
        ret[-1] = self.title
        return tuple(ret)

    @classmethod
    def of(cls, sn: SysNet) -> Self:
        """Resource meta info from sysnet."""
        tokens = sn.meta
        pubs = [n for n in tokens if n.type == "PUBLISHED"]
        if len(pubs) > 1:
            msg = "公開日(@published)は１つまで"
            raise ValueError(msg, pubs)
        pub = None if len(pubs) == 0 else parse2dt(pubs[0])
        return cls(
            authors=[str(n) for n in tokens if n.type == "AUTHOR"],
            urls=[str(n) for n in tokens if n.type == "URL"],
            published=pub,
            title=sn.root,
        )
