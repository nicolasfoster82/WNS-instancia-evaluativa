from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from src.ingest.db import DEFAULT_ENV_FILE, connect_postgres


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
