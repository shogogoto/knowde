"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde._feature._shared import ErrorHandlingMiddleware
from knowde._feature.reference import chap_router, ref_router
from knowde.feature import def_router

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(def_router)
api.include_router(ref_router)
api.include_router(chap_router)
