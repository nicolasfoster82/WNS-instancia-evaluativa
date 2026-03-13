from __future__ import annotations

from datetime import date

import psycopg
from fastapi import APIRouter, HTTPException, Query

from src.services.calculator import cotizar_receta, list_recetas, serialize_cotizacion


router = APIRouter(prefix="/api", tags=["wns-challenge"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/recetas")
def get_recetas() -> dict[str, list[str]]:
    try:
        return {"recetas": list_recetas()}
    except psycopg.Error as exc:
        raise HTTPException(status_code=500, detail="No se pudo consultar PostgreSQL.") from exc


@router.get("/cotizacion")
def get_cotizacion(
    receta: str = Query(..., description="Nombre de la receta a cotizar."),
    fecha: date = Query(..., description="Fecha de cotizacion en formato YYYY-MM-DD."),
) -> dict[str, object]:
    try:
        result = cotizar_receta(receta, fecha)
        return {"cotizacion": serialize_cotizacion(result)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except psycopg.Error as exc:
        raise HTTPException(status_code=500, detail="No se pudo consultar PostgreSQL.") from exc
