"""用語引用.

QUOTERMが Headとして保存されるバグを見つけて修正した

その修正がQUOTERMによるbelow siblingの無限ループを引き起こした
frontendでリソースページが表示できなくなった

DBの変更 Quoterm node classを作成
quoterm関係を削除

Quotermは uidのみを持つ空のnode
KNodeにもQuotermを追加

resource_detailでは termsのようにQuotermのセットも返すようにする

quoterms set = {
    quo_uid: sentence_uid
}

sysnetの第一級の要素に変更(KNodeに追加)
    Termと同等


------------------------------------------------------------------- test
restore_sysnetがうまくいく

quotermであると分かるし、即時その引用元を返せる

"""
