"""系:知識ネットワークの単位.

用語の有効範囲でもある



diff: 系同士の比較
    系の同一性とは何か
        同一の系
            同じrootsを持つ
        異なる系
    意味のあるdiffとは何か
    統合化(unification)支援

統合化モデルとしての評価
    第一文の総数
    文同士の繋がりの総数

データをどう変換していくか
    テキスト
    chunkのリスト
    再帰的に分解
        section 名前解決の対象ではない
        term
            原子名の集まり
        sentence
        term-sentence
    名前解決: 原子名を辿ってnamechain作成


データ変換の結果、何を見たいのか
    検索キーワードと関連のあるデータ


chunk: 見出しやindentに対応するまとまり
    入れ子となる
    メンバを持つ
        メンバは自身、

        line: 一行に相当
            機能:
            marked/unmarked
            has_mark

    変換機能:
        用語一覧
        stmt一覧
        知識ネットワーク
            nodeの種類
                見出し
                用語解決
                    不要 /必要
                    member: 用語/文　// 用語自体にも用語を参照できる
                    時点 // 時系列生成に使える
            edgeの種類
                member
                namechain
                その他context関係
            時系列
                用語
                文
                混合

system: 系
    system名
    chunkのroot

    変換機能:
        markdownへ
        .knへ
        .stageへ
        統合モデルの評価
        chunkの変換の再帰的適用
    機能:
        ネットワークから関連を辿る
            root一覧
            premise, 距離指定可能
            postmise, 距離指定可能 // premiseに対応する造語
            namechain // 用語解決
        位置座標: ネットワーク上での位置づけ
            DBから直接取得できるようにしたい
                それと結果が一致するか

model: 系を別のまとめ直す感じの系
    system間の共通する構造
    読書記録とその整理を分離できる

    sources: 関連付ける系

--- I/O
load: データからメモリ表現を得る
    テキストからparse
    DBから読み取り
    stageから読み取り

stage: 永続化とメモリの中間一時ファイル
    編集による差分を確認したい
    まだ永続化したくないけど保存したい
    auto save
        version管理も
    このローカル運用もできるはず

save: DBへ永続化


posting: テキスト出力
    ブログの自動生成


"""
