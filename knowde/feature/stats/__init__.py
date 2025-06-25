"""高々数個のfeature.parsing.primitive.依存したパッケージ.

体系間の共通する構造.
読書記録とその整理を分離できる
sources: 関連付ける系


class SystemPresenter(BaseModel):
    体系を永続化や統合度など統計値などに変換.

    # def __call__(self, sys: System):
    #     pass

    def load(self) -> None:
        ...

    def stage(self) -> None:
        ...
"""
