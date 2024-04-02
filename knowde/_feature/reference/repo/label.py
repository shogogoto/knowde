from neomodel import DateProperty, One, StringProperty

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.rel_label import RelOrder
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.reference.domain import Book, Web


# Referenceは議論や主張をsポートするための情報源というニュアンス
# Sourceは情報の発信元というニュアンス
# Referenceは3段階構成としてそれ以上の階層は作成しない
# (:Reference)-->(:Chapter)-->(:Section)
# これ以上の階層は分かり易さに寄与しないと思う
# 巨大なRefは複数個に分けて作成する
class LReference(LBase):
    __label__ = "Reference"
    __abstract_node__ = True
    title = StringProperty(index=True)


class LBook(LReference):
    __label__ = "Book"
    first_edited = DateProperty()


class LWeb(LReference):
    __label__ = "Web"
    url = StringProperty()


class LChapter(LBase):
    """章:Ref直下."""

    __label__ = "Chapter"
    value = StringProperty()


class LSection(LBase):
    """節:章の直下."""

    __label__ = "Section"
    value = StringProperty()


BookUtil = LabelUtil(label=LBook, model=Book)
WebUtil = LabelUtil(label=LWeb, model=Web)

RelChapterBookUtil = RelUtil(
    t_source=LBook,
    t_target=LChapter,
    name="COMPOSE",
    t_rel=RelOrder,
    cardinality=One,
)

RelChapterWebUtil = RelUtil(
    t_source=LWeb,
    t_target=LChapter,
    name="COMPOSE",
    t_rel=RelOrder,
    cardinality=One,
)

RelSectionUtil = RelUtil(
    t_target=LSection,
    t_source=LChapter,
    name="COMPOSE",
    t_rel=RelOrder,
    cardinality=One,
)
