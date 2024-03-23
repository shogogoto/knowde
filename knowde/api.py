"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde._feature._shared import ErrorHandlingMiddleware
from knowde.feature import def_router

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(def_router)
