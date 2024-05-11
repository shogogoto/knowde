
from neomodel import DateProperty, One, StringProperty

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.rel_label import RelOrder
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.reference.domain import Book, Chapter, Section, Web


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
ChapterUtil = LabelUtil(label=LChapter, model=Chapter)
SectionUtil = LabelUtil(label=LSection, model=Section)


# 章は１つの本にのみ属す
RelChapterBookUtil = RelUtil(
    t_source=LChapter,
    t_target=LBook,
    name="COMPOSE",
    t_rel=RelOrder,
    cardinality=One,
)

RelChapterWebUtil = RelUtil(
    t_source=LChapter,
    t_target=LWeb,
    name="COMPOSE",
    t_rel=RelOrder,
    cardinality=One,
)

RelSectionUtil = RelUtil(
    t_target=LChapter,
    t_source=LSection,
    name="COMPOSE",
    t_rel=RelOrder,
    cardinality=One,
)
