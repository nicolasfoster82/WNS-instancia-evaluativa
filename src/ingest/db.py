from __future__ import annotations

import os
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_DB_SETTINGS = {
    "host": "localhost",
    "port": 5432,
    "dbname": "wns_challenge",
    "user": "wns_user",
    "password": "wns_password",
}
DB_ENV_MAP = {
    "POSTGRES_HOST": "host",
    "POSTGRES_PORT": "port",
    "POSTGRES_DB": "dbname",
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "password",
}


def read_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def load_connection_settings(env_path: Path = DEFAULT_ENV_FILE) -> dict[str, object]:
    settings = dict(DEFAULT_DB_SETTINGS)
    file_values = read_env_file(env_path)

    for env_key, setting_key in DB_ENV_MAP.items():
        if env_key in file_values:
            settings[setting_key] = file_values[env_key]

    for env_key, setting_key in DB_ENV_MAP.items():
        environment_value = os.getenv(env_key)
        if environment_value:
            settings[setting_key] = environment_value

    settings["port"] = int(settings["port"])
    return settings


def connect_postgres(env_path: Path = DEFAULT_ENV_FILE) -> psycopg.Connection[tuple]:
    return psycopg.connect(**load_connection_settings(env_path))
