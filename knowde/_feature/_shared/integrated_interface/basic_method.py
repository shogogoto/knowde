from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NamedTuple

if TYPE_CHECKING:
    from knowde._feature._shared.integrated_interface.types import CompleteParam
    from knowde._feature._shared.repo.util import LabelUtil


class BasicMethods(NamedTuple):
    complete: Callable
    ls: Callable


def create_basic_methods(
    util: LabelUtil,
) -> BasicMethods:
    def complete(p: CompleteParam) -> util.model:
        return util.complete(p.pref_uid).to_model()

    def ls() -> list[util.model]:
        return util.find_all().to_model()

    return BasicMethods(
        complete=complete,
        ls=ls,
    )
