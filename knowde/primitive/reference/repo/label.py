"""neomodel label."""
from __future__ import annotations

from neomodel import DateProperty, One, StringProperty

from knowde.core import LBase
from knowde.core.repo.rel import RelUtil
from knowde.core.repo.rel_label import RelOrder
from knowde.core.repo.util import LabelUtil
from knowde.primitive.reference.domain import (
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
    """引用."""

    __label__ = "Reference"
    __abstract_node__ = True


class LBook(LReference):
    """本."""

    __label__ = "Book"
    title = StringProperty(index=True, required=True)
    first_edited = DateProperty()


class LWeb(LReference):
    """ウェブリソース."""

    __label__ = "Web"
    title = StringProperty(index=True, required=True)
    url = StringProperty()


class LChapter(LReference):
    """章:Ref直下."""

    __label__ = "Chapter"
    title = StringProperty(required=True)


class LSection(LReference):
    """節:章の直下."""

    __label__ = "Section"
    title = StringProperty(required=True)


BookUtil = LabelUtil(label=LBook, model=Book)
WebUtil = LabelUtil(label=LWeb, model=Web)
ReferenceUtil = LabelUtil(label=LReference, model=Reference)
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


def refroot_type(r: LWeb | LBook) -> RefType:  # noqa: D103
    if isinstance(r, LBook):
        return RefType.Book
    return RefType.Web


def to_refmodel(r: LReference) -> Reference:  # noqa: D103
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
