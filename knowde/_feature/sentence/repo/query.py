from __future__ import annotations

from knowde._feature._shared.repo.label import Label, Labels
from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence


class SentenceQuery:
    @staticmethod
    def find(v: str) -> Labels[LSentence, Sentence]:
        lbs = LSentence.nodes.filter(value__icontains=v)
        return Labels(root=lbs, model=Sentence)

    @staticmethod
    def find_one_or_none(v: str) -> Label[LSentence, Sentence] | None:
        lb = LSentence.nodes.get_or_none(value__icontains=v)
        if lb is None:
            return None
        return Label(label=lb, model=Sentence)
