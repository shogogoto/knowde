"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde._feature import (
    concept_adj_router,
    concept_dest_router,
    concept_router,
    concept_src_router,
    ref_router,
    s_router,
)
from knowde._feature._shared import ErrorHandlingMiddleware
from knowde.feature import def_router

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(concept_router)
api.include_router(concept_adj_router)
api.include_router(concept_src_router)
api.include_router(concept_dest_router)

api.include_router(ref_router)
api.include_router(s_router)
api.include_router(def_router)
