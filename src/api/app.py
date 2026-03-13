from __future__ import annotations

from fastapi import FastAPI

from src.api.routes import router


app = FastAPI(
    title="WNS Challenge API",
    description="API para listar recetas y cotizar platos consumiendo PostgreSQL.",
    version="1.0.0",
)
app.include_router(router)
