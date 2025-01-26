"""root api."""
from __future__ import annotations

import os

from fastapi import FastAPI
from neomodel import config

from knowde.primitive import (
    tl_router,
)
from knowde.primitive.__core__ import ErrorHandlingMiddleware
from knowde.tmp import deduct_router, def_router
from knowde.tmp.deduction.proposition import p_router

config.DATABASE_URL = os.environ["NEO4J_URL"]

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(def_router)
api.include_router(p_router)
api.include_router(deduct_router)
api.include_router(tl_router)
