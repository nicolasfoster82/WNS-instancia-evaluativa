from __future__ import annotations

import unicodedata
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from src.ingest.db import DEFAULT_ENV_FILE, connect_postgres
from src.services.exchange_rate import fetch_usd_to_ars_rate


PURCHASE_STEP_GRAMS = 250
GRAMS_PER_KILOGRAM = Decimal("1000")
MONEY_STEP = Decimal("0.01")


def _normalize_lookup(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.casefold().split())


def _to_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_STEP, rounding=ROUND_HALF_UP)


def _validate_quote_date(quote_date: date) -> None:
    today = date.today()
    oldest_allowed = today - timedelta(days=30)
    if quote_date < oldest_allowed or quote_date > today:
        raise ValueError(
            "La fecha debe estar entre "
            f"{oldest_allowed.isoformat()} y {today.isoformat()}."
        )


def _round_purchase_quantity(quantity_grams: int) -> int:
    return ((quantity_grams + PURCHASE_STEP_GRAMS - 1) // PURCHASE_STEP_GRAMS) * PURCHASE_STEP_GRAMS


def _fetch_recipe_names(cursor) -> list[str]:
    cursor.execute("SELECT nombre FROM recetas ORDER BY nombre")
    return [str(nombre) for (nombre,) in cursor.fetchall()]


def list_recetas(env_path: Path = DEFAULT_ENV_FILE) -> list[str]:
    with connect_postgres(env_path) as connection:
        with connection.cursor() as cursor:
            return _fetch_recipe_names(cursor)


def _resolve_recipe_name(cursor, recipe_name: str) -> str:
    recipe_names = _fetch_recipe_names(cursor)
    normalized_index = {_normalize_lookup(name): name for name in recipe_names}
    actual_name = normalized_index.get(_normalize_lookup(recipe_name))
    if actual_name is None:
        disponibles = ", ".join(recipe_names)
        raise ValueError(
            "No se encontro la receta solicitada. "
            f"Recetas disponibles: {disponibles}"
        )
    return actual_name


def _load_recipe_rows(cursor, recipe_name: str) -> list[tuple]:
    actual_name = _resolve_recipe_name(cursor, recipe_name)
    cursor.execute(
        """
        SELECT
            r.nombre,
            COALESCE(r.instrucciones, ''),
            p.nombre,
            ri.cantidad_gramos,
            p.precio_kg_ars
        FROM recetas r
        JOIN receta_ingredientes ri ON ri.id_receta = r.id_receta
        JOIN productos p ON p.id_producto = ri.id_producto
        WHERE r.nombre = %s
        ORDER BY ri.id_receta_ingrediente
        """,
        (actual_name,),
    )
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"La receta '{actual_name}' no tiene ingredientes cargados.")
    return rows


def cotizar_receta(
    recipe_name: str,
    quote_date: date,
    env_path: Path = DEFAULT_ENV_FILE,
) -> dict[str, object]:
    _validate_quote_date(quote_date)

    with connect_postgres(env_path) as connection:
        with connection.cursor() as cursor:
            rows = _load_recipe_rows(cursor, recipe_name)

    ars_per_usd = Decimal(fetch_usd_to_ars_rate(quote_date, env_path))
    ingredientes: list[dict[str, object]] = []
    total_ars = Decimal("0")

    for _, _, ingredient_name, quantity_grams, price_per_kilo_ars in rows:
        purchase_quantity_grams = _round_purchase_quantity(int(quantity_grams))
        subtotal_ars = _to_money(
            (Decimal(purchase_quantity_grams) / GRAMS_PER_KILOGRAM) * Decimal(price_per_kilo_ars)
        )
        total_ars += subtotal_ars
        ingredientes.append(
            {
                "nombre_producto": str(ingredient_name),
                "cantidad_receta_gramos": int(quantity_grams),
                "cantidad_compra_gramos": purchase_quantity_grams,
                "precio_kg_ars": _to_money(Decimal(price_per_kilo_ars)),
                "subtotal_ars": subtotal_ars,
            }
        )

    total_ars = _to_money(total_ars)
    total_usd = _to_money(total_ars / ars_per_usd)
    recipe_name, instructions, *_ = rows[0]

    return {
        "receta": str(recipe_name),
        "fecha": quote_date.isoformat(),
        "cotizacion_usd_ars": ars_per_usd,
        "instrucciones": str(instructions),
        "ingredientes": ingredientes,
        "total_ars": total_ars,
        "total_usd": total_usd,
    }


def serialize_cotizacion(result: dict[str, object]) -> dict[str, object]:
    return {
        "receta": result["receta"],
        "fecha": result["fecha"],
        "cotizacion_usd_ars": str(result["cotizacion_usd_ars"]),
        "instrucciones": result["instrucciones"],
        "ingredientes": [
            {
                "nombre_producto": ingrediente["nombre_producto"],
                "cantidad_receta_gramos": ingrediente["cantidad_receta_gramos"],
                "cantidad_compra_gramos": ingrediente["cantidad_compra_gramos"],
                "precio_kg_ars": str(ingrediente["precio_kg_ars"]),
                "subtotal_ars": str(ingrediente["subtotal_ars"]),
            }
            for ingrediente in result["ingredientes"]
        ],
        "total_ars": str(result["total_ars"]),
        "total_usd": str(result["total_usd"]),
    }
