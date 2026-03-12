from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from src.ingest.db import DEFAULT_ENV_FILE, connect_postgres
from src.parsers.carnes_pescados import DEFAULT_INPUT, parse_carnes_pescados

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _upsert_categoria(cursor, nombre: str) -> int:
    cursor.execute(
        """
        INSERT INTO categorias (nombre)
        VALUES (%s)
        ON CONFLICT (nombre) DO UPDATE
        SET nombre = EXCLUDED.nombre
        RETURNING id_categoria
        """,
        (nombre,),
    )
    return int(cursor.fetchone()[0])


def _upsert_subcategoria(cursor, categoria_id: int, nombre: str) -> int:
    cursor.execute(
        """
        INSERT INTO subcategorias (id_categoria, nombre)
        VALUES (%s, %s)
        ON CONFLICT (id_categoria, nombre) DO UPDATE
        SET nombre = EXCLUDED.nombre
        RETURNING id_subcategoria
        """,
        (categoria_id, nombre),
    )
    return int(cursor.fetchone()[0])


def _upsert_producto(cursor, subcategoria_id: int, producto: dict[str, object]) -> int:
    cursor.execute(
        """
        INSERT INTO productos (id_subcategoria, nombre, precio_kg_ars, es_estacional)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_subcategoria, nombre) DO UPDATE
        SET precio_kg_ars = EXCLUDED.precio_kg_ars,
            es_estacional = EXCLUDED.es_estacional
        RETURNING id_producto
        """,
        (
            subcategoria_id,
            str(producto["nombre"]),
            Decimal(str(producto["precio_kg_ars"])),
            bool(producto.get("es_estacional", False)),
        ),
    )
    return int(cursor.fetchone()[0])


def ingest_productos(productos: list[dict[str, object]], env_path: Path = DEFAULT_ENV_FILE) -> dict[str, int]:
    categorias: dict[str, int] = {}
    subcategorias: dict[tuple[int, str], int] = {}
    productos_procesados = 0

    with connect_postgres(env_path) as connection:
        with connection.cursor() as cursor:
            for producto in productos:
                categoria_nombre = str(producto["categoria"])
                categoria_id = categorias.get(categoria_nombre)
                if categoria_id is None:
                    categoria_id = _upsert_categoria(cursor, categoria_nombre)
                    categorias[categoria_nombre] = categoria_id

                subcategoria_nombre = str(producto["subcategoria"])
                subcategoria_key = (categoria_id, subcategoria_nombre)
                subcategoria_id = subcategorias.get(subcategoria_key)
                if subcategoria_id is None:
                    subcategoria_id = _upsert_subcategoria(cursor, categoria_id, subcategoria_nombre)
                    subcategorias[subcategoria_key] = subcategoria_id

                _upsert_producto(cursor, subcategoria_id, producto)
                productos_procesados += 1

        connection.commit()

    return {
        "categorias": len(categorias),
        "subcategorias": len(subcategorias),
        "productos": productos_procesados,
    }


def ingest_carnes_pescados(
    file_path: Path = DEFAULT_INPUT,
    env_path: Path = DEFAULT_ENV_FILE,
) -> dict[str, object]:
    productos = parse_carnes_pescados(file_path)
    result = ingest_productos(productos, env_path)
    result["archivo"] = str(file_path)
    return result


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest inputs/Carnes y Pescados.xlsx into PostgreSQL")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the xlsx file to ingest.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the env file with PostgreSQL connection settings.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the ingestion result as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = ingest_carnes_pescados(args.input, args.env_file)
    if args.json:
        print(
            json.dumps(
                {
                    "archivo": _display_path(args.input),
                    "env_file": _display_path(args.env_file),
                    "resultado": {
                        "categorias": result["categorias"],
                        "subcategorias": result["subcategorias"],
                        "productos": result["productos"],
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(f"Archivo fuente: {_display_path(args.input)}")
        print(f"Archivo de entorno: {_display_path(args.env_file)}")
        print("")
        print("Resultado de la ingesta:")
        print(f"- Categorias procesadas: {result['categorias']}")
        print(f"- Subcategorias procesadas: {result['subcategorias']}")
        print(f"- Productos procesados: {result['productos']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
