from __future__ import annotations

import argparse
from pathlib import Path

import psycopg
from psycopg import sql

from src.ingest.carnes_pescados import ingest_carnes_pescados
from src.ingest.db import DEFAULT_ENV_FILE, PROJECT_ROOT, connect_postgres, load_connection_settings
from src.ingest.recetas import ingest_recetas
from src.ingest.verduleria import ingest_verduleria


DEFAULT_SCHEMA_FILE = PROJECT_ROOT / "docker" / "postgres" / "init" / "01_schema.sql"
MAINTENANCE_DATABASES = ("postgres", "template1")


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _connect_maintenance_database(env_path: Path = DEFAULT_ENV_FILE) -> psycopg.Connection[tuple]:
    settings = load_connection_settings(env_path)
    errors: list[str] = []

    for database_name in MAINTENANCE_DATABASES:
        try:
            return psycopg.connect(
                host=str(settings["host"]),
                port=int(settings["port"]),
                dbname=database_name,
                user=str(settings["user"]),
                password=str(settings["password"]),
            )
        except psycopg.OperationalError as exc:
            errors.append(f"{database_name}: {exc}")

    raise RuntimeError(
        "No se pudo conectar a una base de mantenimiento de PostgreSQL. "
        f"Intentos: {' | '.join(errors)}"
    )


def ensure_database(env_path: Path = DEFAULT_ENV_FILE) -> dict[str, object]:
    settings = load_connection_settings(env_path)
    target_database = str(settings["dbname"])

    with _connect_maintenance_database(env_path) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_database,))
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_database))
                )

    return {
        "database": target_database,
        "created": not exists,
    }


def _table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (table_name,),
    )
    return cursor.fetchone() is not None


def ensure_schema(
    schema_path: Path = DEFAULT_SCHEMA_FILE,
    env_path: Path = DEFAULT_ENV_FILE,
) -> dict[str, object]:
    with connect_postgres(env_path) as connection:
        with connection.cursor() as cursor:
            if _table_exists(cursor, "categorias"):
                return {
                    "schema_file": str(schema_path),
                    "applied": False,
                }

            cursor.execute(schema_path.read_text(encoding="utf-8"))
        connection.commit()

    return {
        "schema_file": str(schema_path),
        "applied": True,
    }


def bootstrap_data(env_path: Path = DEFAULT_ENV_FILE) -> dict[str, object]:
    carnes_result = ingest_carnes_pescados(env_path=env_path)
    verduleria_result = ingest_verduleria(env_path=env_path)
    recetas_result = ingest_recetas(env_path=env_path)

    return {
        "carnes_pescados": {
            "categorias": carnes_result["categorias"],
            "subcategorias": carnes_result["subcategorias"],
            "productos": carnes_result["productos"],
        },
        "verduleria": {
            "categorias": verduleria_result["categorias"],
            "subcategorias": verduleria_result["subcategorias"],
            "productos": verduleria_result["productos"],
        },
        "recetas": {
            "recetas": recetas_result["recetas"],
            "ingredientes": recetas_result["ingredientes"],
        },
    }


def bootstrap_project(
    env_path: Path = DEFAULT_ENV_FILE,
    schema_path: Path = DEFAULT_SCHEMA_FILE,
) -> dict[str, object]:
    database_result = ensure_database(env_path)
    schema_result = ensure_schema(schema_path, env_path)
    data_result = bootstrap_data(env_path)

    return {
        "database": database_result,
        "schema": schema_result,
        "data": data_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the PostgreSQL database, apply the schema and ingest all sources."
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the env file with PostgreSQL connection settings.",
    )
    parser.add_argument(
        "--schema-file",
        type=Path,
        default=DEFAULT_SCHEMA_FILE,
        help="Path to the SQL schema file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = bootstrap_project(args.env_file, args.schema_file)

    print(f"Archivo de entorno: {_display_path(args.env_file)}")
    print(f"Schema SQL: {_display_path(args.schema_file)}")
    print("")
    print("Base de datos:")
    print(f"- Nombre: {result['database']['database']}")
    print(
        "- Creada por bootstrap en esta ejecucion: "
        f"{'si' if result['database']['created'] else 'no'}"
    )
    print("")
    print("Schema:")
    print(
        "- Aplicado por bootstrap en esta ejecucion: "
        f"{'si' if result['schema']['applied'] else 'no'}"
    )
    print("")
    print("Carga de datos:")
    print(
        "- Carnes y pescados: "
        f"{result['data']['carnes_pescados']['productos']} productos"
    )
    print(
        "- Verduleria: "
        f"{result['data']['verduleria']['productos']} productos"
    )
    print(
        "- Recetas: "
        f"{result['data']['recetas']['recetas']} recetas y "
        f"{result['data']['recetas']['ingredientes']} ingredientes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
