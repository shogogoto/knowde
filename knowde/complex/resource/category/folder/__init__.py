"""sysnetの管理.

モチベは?


userId/folder
    CRUD

    root folder user直下
    folder は 配下ではnameが重複してはならない
    rename
    remove 配下のフォルダとsysnetも全て削除
    move parentを差し替える

    folderのCRUD
    folderとCLIのsync upload
        変更があったか否かを低コストでチェックできるとよい
            sysnet のhash値とか使える?

        find コマンドとの連携を考えるか
            自前で作らない方がいい

    folder と CLI userのディレクトリの同期
        CLI find して ファイルパスの構造をそのままsync(永続化)
          -> Git管理できて便利

"""
