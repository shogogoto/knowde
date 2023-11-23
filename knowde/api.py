"""api root."""
from __future__ import annotations

from fastapi import FastAPI

from ._feature import concept_router

api = FastAPI()
api.include_router(concept_router)
