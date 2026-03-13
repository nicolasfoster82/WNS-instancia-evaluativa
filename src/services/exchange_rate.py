from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from src.ingest.db import DEFAULT_ENV_FILE, read_env_file


DEFAULT_CURRENCY_API_URLS = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/usd.json",
    "https://{date}.currency-api.pages.dev/v1/currencies/usd.json",
]
CURRENCY_API_URLS_ENV = "CURRENCY_API_URLS"


def _parse_currency_api_urls(raw_value: str) -> list[str]:
    return [url.strip() for url in raw_value.split(",") if url.strip()]


def load_currency_api_urls(env_path: Path = DEFAULT_ENV_FILE) -> list[str]:
    file_values = read_env_file(env_path)
    raw_value = os.getenv(CURRENCY_API_URLS_ENV) or file_values.get(CURRENCY_API_URLS_ENV, "")
    configured_urls = _parse_currency_api_urls(raw_value)
    return configured_urls or list(DEFAULT_CURRENCY_API_URLS)


def fetch_usd_to_ars_rate(quote_date: date, env_path: Path = DEFAULT_ENV_FILE) -> str:
    errors: list[str] = []

    for template in load_currency_api_urls(env_path):
        url = template.format(date=quote_date.isoformat())
        try:
            with urlopen(url, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return str(payload["usd"]["ars"])
        except KeyError:
            errors.append(f"{url}: faltan claves usd/ars")
        except ValueError:
            errors.append(f"{url}: cotizacion invalida")
        except HTTPError as exc:
            errors.append(f"{url}: HTTP {exc.code}")
        except URLError as exc:
            errors.append(f"{url}: {exc.reason}")
        except json.JSONDecodeError:
            errors.append(f"{url}: respuesta JSON invalida")

    raise RuntimeError(
        "No se pudo obtener la cotizacion USD/ARS desde ninguno de los endpoints configurados. "
        f"Intentos: {' | '.join(errors)}"
    )
