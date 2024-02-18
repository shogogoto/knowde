"""new create repository."""
from neomodel import OUTGOING, RelationshipDefinition

from knowde._feature.sentence import SentenceQuery, s_util
from knowde._feature.sentence.repo.label import LSentence
from knowde._feature.term import TermQuery, term_util

RelationshipDefinition(
    relation_type="DEFINE",
    cls_name=LSentence.__class__.__name__,
    direction=OUTGOING,
)


def define(name: str, explain: str) -> None:
    """Create new defenition."""
    term = TermQuery.find_one_or_none(name)
    s = SentenceQuery.find_one_or_none(explain)
    if term is None:
        term = term_util.create(value=name)
    if s is None:
        s = s_util.create(value=explain)

    # Traversal
