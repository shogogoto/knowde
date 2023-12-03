"""api root."""
from __future__ import annotations

from fastapi import FastAPI

from ._feature import (
    concept_adj_router,
    concept_dest_router,
    concept_router,
    concept_src_router,
)

api = FastAPI()
api.include_router(concept_router)
api.include_router(concept_adj_router)
api.include_router(concept_src_router)
api.include_router(concept_dest_router)
