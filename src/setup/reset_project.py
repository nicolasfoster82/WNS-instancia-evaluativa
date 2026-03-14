from __future__ import annotations

import argparse
from pathlib import Path

import psycopg
from psycopg import sql

from src.ingest.db import DEFAULT_ENV_FILE, load_connection_settings


MAINTENANCE_DATABASES = ("postgres", "template1")


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


def drop_project_database(env_path: Path = DEFAULT_ENV_FILE) -> dict[str, object]:
    settings = load_connection_settings(env_path)
    target_database = str(settings["dbname"])

    with _connect_maintenance_database(env_path) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_database,))
            exists = cursor.fetchone() is not None

            if exists:
                cursor.execute(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = %s
                      AND pid <> pg_backend_pid()
                    """,
                    (target_database,),
                )
                cursor.execute(
                    sql.SQL("DROP DATABASE {}").format(sql.Identifier(target_database))
                )

    return {
        "database": target_database,
        "dropped": exists,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drop the project PostgreSQL database if it exists."
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
    result = drop_project_database(args.env_file)

    print("Reset local de PostgreSQL:")
    print(f"- Base objetivo: {result['database']}")
    print(f"- Eliminada en esta ejecucion: {'si' if result['dropped'] else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
