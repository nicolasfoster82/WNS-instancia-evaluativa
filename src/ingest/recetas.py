from __future__ import annotations

import argparse
from pathlib import Path

from src.ingest.db import DEFAULT_ENV_FILE, connect_postgres
from src.parsers.recetas import DEFAULT_INPUT, parse_recetas


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _build_product_index(cursor) -> dict[str, int]:
    cursor.execute("SELECT id_producto, nombre FROM productos ORDER BY nombre")
    return {str(nombre): int(producto_id) for producto_id, nombre in cursor.fetchall()}


def _upsert_receta(cursor, receta: dict[str, object]) -> int:
    cursor.execute(
        """
        INSERT INTO recetas (nombre, instrucciones)
        VALUES (%s, %s)
        ON CONFLICT (nombre) DO UPDATE
        SET instrucciones = EXCLUDED.instrucciones
        RETURNING id_receta
        """,
        (
            str(receta["nombre"]),
            str(receta["instrucciones"]),
        ),
    )
    return int(cursor.fetchone()[0])


def _replace_recipe_ingredients(
    cursor,
    receta_id: int,
    ingredientes: list[dict[str, object]],
    product_index: dict[str, int],
) -> int:
    cursor.execute("DELETE FROM receta_ingredientes WHERE id_receta = %s", (receta_id,))

    ingredientes_insertados = 0
    ingredientes_faltantes: list[str] = []

    for ingrediente in ingredientes:
        nombre_producto = str(ingrediente["nombre_producto"])
        producto_id = product_index.get(nombre_producto)
        if producto_id is None:
            ingredientes_faltantes.append(nombre_producto)
            continue

        cursor.execute(
            """
            INSERT INTO receta_ingredientes (id_receta, id_producto, cantidad_gramos)
            VALUES (%s, %s, %s)
            """,
            (
                receta_id,
                producto_id,
                int(ingrediente["cantidad_gramos"]),
            ),
        )
        ingredientes_insertados += 1

    if ingredientes_faltantes:
        faltantes = ", ".join(sorted(ingredientes_faltantes))
        raise ValueError(f"No se encontraron productos para estos ingredientes: {faltantes}")

    return ingredientes_insertados


def ingest_recetas(
    file_path: Path = DEFAULT_INPUT,
    env_path: Path = DEFAULT_ENV_FILE,
) -> dict[str, object]:
    payload = parse_recetas(file_path)

    with connect_postgres(env_path) as connection:
        with connection.cursor() as cursor:
            product_index = _build_product_index(cursor)
            recetas_procesadas = 0
            ingredientes_procesados = 0

            for receta in payload:
                receta_id = _upsert_receta(cursor, receta)
                ingredientes_procesados += _replace_recipe_ingredients(
                    cursor,
                    receta_id,
                    receta["ingredientes"],
                    product_index,
                )
                recetas_procesadas += 1

        connection.commit()

    return {
        "archivo": str(file_path),
        "recetas": recetas_procesadas,
        "ingredientes": ingredientes_procesados,
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest inputs/Recetas.md into PostgreSQL")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the markdown file to ingest.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the env file with PostgreSQL connection settings.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = ingest_recetas(args.input, args.env_file)
    print(f"Archivo fuente: {_display_path(args.input)}")
    print(f"Archivo de entorno: {_display_path(args.env_file)}")
    print("")
    print("Resultado de la ingesta:")
    print(f"- Recetas procesadas: {result['recetas']}")
    print(f"- Ingredientes procesados: {result['ingredientes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
