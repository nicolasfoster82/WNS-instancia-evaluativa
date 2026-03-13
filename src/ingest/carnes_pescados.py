from __future__ import annotations

import argparse
from pathlib import Path

from src.ingest.db import DEFAULT_ENV_FILE
from src.ingest.productos import ingest_productos
from src.parsers.carnes_pescados import DEFAULT_INPUT, parse_carnes_pescados

PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = ingest_carnes_pescados(args.input, args.env_file)
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
