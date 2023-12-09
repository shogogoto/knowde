from __future__ import annotations

from typing import Annotated, Any

from pydantic import (
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
)

from knowde._feature._shared.repo.base import LBase


def _validate_neomodel(
    v: Any,  # noqa: ANN401
    info: ValidationInfo,  # noqa: ARG001
) -> LBase:
    if isinstance(v, LBase):
        return v
    raise TypeError


NeoModel = Annotated[
    LBase,
    PlainValidator(_validate_neomodel),
    PlainSerializer(lambda x: x.__properties__),
]
