"""用語引用domain."""

from knowde.shared.types import Duplicable


class Quoterm(Duplicable, frozen=True):
    """用語引用.

    ``で用語を囲むことで、その文の参照を置き、別ページなど他の場所で関連を作成できる
    """
