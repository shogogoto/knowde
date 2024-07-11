"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde._feature import book_router, chap_router, ref_router, sec_router, tl_router
from knowde._feature._shared import ErrorHandlingMiddleware
from knowde._feature.proposition import p_router
from knowde.feature import deduct_router, def_router
from knowde.reference import refdef_router

api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)

api.include_router(def_router)
api.include_router(ref_router)
api.include_router(book_router)
api.include_router(chap_router)
api.include_router(sec_router)
api.include_router(refdef_router)

api.include_router(p_router)
api.include_router(deduct_router)

api.include_router(tl_router)
