"""userに所有されたsysnet.

URL
{user_id}/path/title/文
{user_id}/path/sentences
{user_id}/path/defs
とかでresource横断で表を取得できる

indicator 文の位置づけを意味するpath
    userId/folder/title(H1)/h2...h6/文
        title前 userId / folder
        title後 見出し // URLには含めないでおこう、長くなりすぎそう
    文脈はindicatorには含まない

Todo:
----
    folderのCRUD
    folderとCLIのsync upload
        変更があったか否かを低コストでチェックできるとよい
            sysnet のhash値とか使える?

        find コマンドとの連携を考えるか
            自前で作らない方がいい


"""


from knowde.primitive.user import BaseMapper


class Resource(BaseMapper):
    """sysnetの永続化."""
