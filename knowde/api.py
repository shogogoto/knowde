"""root api."""
from __future__ import annotations

from fastapi import FastAPI

from knowde.complex import deduct_router, def_router, ev_router, person_router
from knowde.core import ErrorHandlingMiddleware
from knowde.primitive import (
    book_router,
    chap_router,
    loc_router,
    ref_router,
    sec_router,
    tl_router,
)
from knowde.primitive.proposition import p_router
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
api.include_router(loc_router)
api.include_router(person_router)
api.include_router(ev_router)
