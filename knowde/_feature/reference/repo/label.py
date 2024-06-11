from __future__ import annotations

from neomodel import DateProperty, One, StringProperty

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.rel_label import RelOrder
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.reference.domain import (
    Book,
    Chapter,
    Reference,
    RefType,
    Section,
    Web,
)


# Referenceは議論や主張をsポートするための情報源というニュアンス
# Sourceは情報の発信元というニュアンス
# Referenceは3段階構成としてそれ以上の階層は作成しない
# (:Reference)-->(:Chapter)-->(:Section)
# これ以上の階層は分かり易さに寄与しないと思う
# 巨大なRefは複数個に分けて作成する
class LReference(LBase):
    __label__ = "Reference"
    __abstract_node__ = True


class LBook(LReference):
    __label__ = "Book"
    title = StringProperty(index=True)
    first_edited = DateProperty()


class LWeb(LReference):
    __label__ = "Web"
    title = StringProperty(index=True)
    url = StringProperty()


class LChapter(LReference):
    """章:Ref直下."""

    __label__ = "Chapter"
    title = StringProperty()


class LSection(LReference):
    """節:章の直下."""

    __label__ = "Section"
    title = StringProperty()


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


def refroot_type(r: LWeb | LBook) -> RefType:
    if isinstance(r, LBook):
        return RefType.Book
    return RefType.Web


def to_refmodel(r: LReference) -> Reference:
    if isinstance(r, LBook):
        return Book.to_model(r)
    if isinstance(r, LWeb):
        return Web.to_model(r)
    if isinstance(r, LChapter):
        return Chapter.to_model(r)
    if isinstance(r, LSection):
        return Section.to_model(r)
    msg = f"f{type(r)} must be LReference Type."
    raise TypeError(msg)


# def rel_order2ref(rel: RelOrder) -> Reference:
#     s = rel.start_node()
#     e = rel.end_node()

#     if isinstance(s, LChapter):
#         return Chapter.from_rel(rel)
#     if isinstance(s, LSection):
#         return Section.from_rel(rel)
#     if isinstance(s, LReference):
#         return to_refmodel(s)
#     raise TypeError
