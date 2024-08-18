"""aaa."""
from operator import attrgetter
from uuid import UUID

from knowde.primitive.reference.domain import Section
from knowde.primitive.reference.dto import HeadlineParam, SwapParam
from knowde.primitive.reference.repo.label import (
    ChapterUtil,
    RelSectionUtil,
    SectionUtil,
)


def add_section(chap_uid: UUID, p: HeadlineParam) -> Section:  # noqa: D103
    c = ChapterUtil.find_by_id(chap_uid)
    s = SectionUtil.create(title=p.title)
    count = RelSectionUtil.count_sources(chap_uid)
    rel = RelSectionUtil.connect(s.label, c.label, order=count)
    # return Section.from_rel(rel)
    return Section.to_model(rel.start_node())


def swap_section_order(chap_uid: UUID, p: SwapParam) -> None:  # noqa: D103
    rels = RelSectionUtil.find_by_target_id(chap_uid)
    rel1 = next(filter(lambda x: x.order == p.order1, rels))
    rel2 = next(filter(lambda x: x.order == p.order2, rels))
    rel1.order = p.order2
    rel2.order = p.order1
    rel1.save()
    rel2.save()


def change_section(  # noqa: D103
    sec_uid: UUID,
    p: HeadlineParam,
) -> Section:
    SectionUtil.change(uid=sec_uid, title=p.title)
    rel = RelSectionUtil.find_by_source_id(sec_uid)[0]
    return Section.from_rel(rel=rel)


def remove_section(sec_uid: UUID) -> None:
    """兄弟sectionをreorderしてsectionを削除."""
    rel = RelSectionUtil.find_by_source_id(sec_uid)[0]
    chap_uid = UUID(rel.end_node().uid)
    SectionUtil.delete(sec_uid)
    rels = RelSectionUtil.find_by_target_id(chap_uid)
    rels = sorted(rels, key=attrgetter("order"))
    for i, rel in enumerate(rels):
        rel.order = i
        rel.save()


def complete_section(pref_uid: str) -> Section:  # noqa: D103
    lb = SectionUtil.complete(pref_uid)
    m = lb.to_model()
    rel = RelSectionUtil.find_by_source_id(m.valid_uid)[0]
    return Section.to_model(rel.start_node())
