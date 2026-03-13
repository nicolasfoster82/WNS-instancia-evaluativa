from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import psycopg

from src.ingest.db import DEFAULT_ENV_FILE
from src.services.calculator import cotizar_receta, list_recetas, serialize_cotizacion


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("La fecha debe tener formato YYYY-MM-DD.") from exc


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quote a recipe from PostgreSQL using the historical USD/ARS API."
    )
    parser.add_argument(
        "--receta",
        help="Recipe name to quote. Use --listar-recetas to inspect the available names.",
    )
    parser.add_argument(
        "--fecha",
        type=_parse_date,
        help="Quote date in YYYY-MM-DD format. It must be within the last 30 days.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the env file with PostgreSQL connection settings.",
    )
    parser.add_argument(
        "--listar-recetas",
        action="store_true",
        help="List the available recipes already loaded in PostgreSQL.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the quotation result as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.listar_recetas:
            recetas = list_recetas(args.env_file)
            if args.json:
                print(json.dumps({"recetas": recetas}, indent=2, ensure_ascii=False))
            else:
                print("Recetas disponibles:")
                for receta in recetas:
                    print(f"- {receta}")
            return 0

        if not args.receta or not args.fecha:
            raise SystemExit(
                "Debes indicar --receta y --fecha, o usar --listar-recetas para ver las opciones."
            )

        result = cotizar_receta(args.receta, args.fecha, args.env_file)

        if args.json:
            print(
                json.dumps(
                    {
                        "env_file": _display_path(args.env_file),
                        "cotizacion": serialize_cotizacion(result),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            print(f"Receta: {result['receta']}")
            print(f"Fecha: {result['fecha']}")
            print(f"Cotizacion USD/ARS: {result['cotizacion_usd_ars']}")
            print("")
            print("Ingredientes:")
            for ingrediente in result["ingredientes"]:
                print(
                    "- "
                    f"{ingrediente['nombre_producto']}: "
                    f"receta {ingrediente['cantidad_receta_gramos']} g, "
                    f"compra {ingrediente['cantidad_compra_gramos']} g, "
                    f"precio/kg ARS {ingrediente['precio_kg_ars']}, "
                    f"subtotal ARS {ingrediente['subtotal_ars']}"
                )
            print("")
            print(f"Total ARS: {result['total_ars']}")
            print(f"Total USD: {result['total_usd']}")
    except (ValueError, RuntimeError, psycopg.Error) as exc:
        raise SystemExit(str(exc)) from exc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
