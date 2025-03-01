"""userに所有されたsysnet.

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


from knowde.primitive.__core__.neoutil import BaseMapper


class Resource(BaseMapper):
    """sysnetの永続化."""
