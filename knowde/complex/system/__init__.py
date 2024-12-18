"""系:知識ネットワークの単位.

統合化(unification)支援
    diff: 系同士の比較
        系の同一性とは何か
            同一の系
                同じrootsを持つ
            異なる系
        意味のあるdiffとは何か
    統合化モデルとしての評価
        第一文の総数
        文同士の繋がりの総数(エッジ総数)
        用語数

    指標 index 有用な情報


データ変換の結果、何を見たいのか
    検索キーワードと関連のあるデータ
    統計値
    統合度
        文字数も欲しいかも


時系列

system: 系
    変換機能:
        markdown
        .kn
        .stage
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
load: sysnetの構築
    from
        テキスト
        DB
        stage: 永続化とメモリの中間一時ファイル
            編集による差分を確認したい
            まだ永続化したくないけど保存したい
            auto save
                version管理も
            このローカル運用もできるはず


posting: テキスト出力
    ブログの自動生成
"""


from pydantic import BaseModel


class SourceInfo(BaseModel):
    """情報源のメタ情報."""


class Model(BaseModel):
    """体系間の共通する構造.

    読書記録とその整理を分離できる

    sources: 関連付ける系
    """

    # sources: list[System]


class SystemPresenter(BaseModel):
    """体系を永続化や統合度など統計値などに変換.

    markdownへ
    .knへ
    統合モデルの評価
    chunkの変換の再帰的適用

    output
        DB
        .stageへ
        stdout

    """

    # def __call__(self, sys: System):
    #     pass

    def load(self) -> None:
        """メモリ表現を得る.

        テキストからparse
        DBから読み取り
        stageから読み取り
        """
        ...

    def stage(self) -> None:
        """永続化とメモリの中間一時ファイル.

        編集による差分を確認したい
        まだ永続化したくないけど保存したい
        auto save
            version管理も
        このローカル運用もできるはず
        """
