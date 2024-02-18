from __future__ import annotations

from knowde._feature.sentence.domain import Sentence
from knowde._feature.sentence.repo.label import LSentence


class SentenceQuery:
    @staticmethod
    def find(v: str) -> list[Sentence]:
        lbs = LSentence.nodes.filter(value__icontains=v)
        return Sentence.to_models(lbs)

    @staticmethod
    def find_one_or_none(v: str) -> Sentence | None:
        lb = LSentence.nodes.get_or_none(value__icontains=v)
        if lb is None:
            return None
        return Sentence.to_model(lb)
