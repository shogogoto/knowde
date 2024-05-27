"""定義と参考文献を紐付けたい.

ref def add [ref_uid|chap_uid|sec_uid] title sentence
ref conn [ref_uid|chap_uid|sec_uid] def_uid
ref disconn [ref_uid|chap_uid|sec_uid] def_uid


Todo:
----
referred def
    refとdefの紐付け
    refでの定義数をカウント
    chapでの定義数のカウント
    secでの定義数のカウント

defの統計値
    defのrootsの取得
        rootsごとの距離も取得
    defのleavesの取得
        leavesごとの居見も取得
    defのsourcesのカウント


"""
