"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde._feature import (
    ref_router,
    s_router,
)
from knowde._feature._shared import ErrorHandlingMiddleware
from knowde.feature import def_router

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(ref_router)
api.include_router(s_router)
api.include_router(def_router)
