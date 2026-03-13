from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router


STATIC_DIR = Path(__file__).resolve().parent / "static"


app = FastAPI(
    title="WNS Challenge API",
    description="API para listar recetas y cotizar platos consumiendo PostgreSQL.",
    version="1.0.0",
)
app.include_router(router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
