"""api root."""
from __future__ import annotations

from fastapi import FastAPI

from .feature import concept_router

app = FastAPI()
app.include_router(concept_router)


@app.get("/")
async def hello() -> dict[str, str]:
    """Any api for deploy test."""
    return {"message": "Hello World"}
