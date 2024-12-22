"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde.complex import deduct_router, def_router
from knowde.complex.deduction.proposition import p_router
from knowde.primitive import (
    tl_router,
)
from knowde.primitive.__core__ import ErrorHandlingMiddleware

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(def_router)
api.include_router(p_router)
api.include_router(deduct_router)
api.include_router(tl_router)
