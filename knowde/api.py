"""api root."""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello() -> dict[str, str]:
    """Any api for deploy test."""
    return {"message": "Hello World"}