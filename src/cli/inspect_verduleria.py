from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.parsers.verduleria import DEFAULT_INPUT, parse_verduleria, summarize_products


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _format_price(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.2f}"


def render_text_report(productos: list[dict[str, object]], file_path: Path) -> str:
    lines = [
        f"Archivo: {_display_path(file_path)}",
        "Librerias externas de Python: pdfplumber",
        "",
        "Resumen propuesto para DB:",
    ]
    summary = summarize_products(productos)
    for categoria, subcategorias in summary.items():
        lines.append(f"- {categoria}:")
        for subcategoria, count in subcategorias.items():
            lines.append(f"  - {subcategoria}: {count} productos")

    lines.extend(["", "Productos normalizados:"])
    for producto in productos:
        estacional = "si" if producto["es_estacional"] else "no"
        lines.append(
            f"- {producto['categoria']} | {producto['subcategoria']} | {producto['nombre']} | "
            f"{_format_price(float(producto['precio_kg_ars']))} ARS/kg | estacional: {estacional}"
        )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and normalize the file inputs/verduleria.pdf")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the pdf file to inspect.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the normalized parse result as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    productos = parse_verduleria(args.input)
    if args.json:
        print(
            json.dumps(
                {
                    "archivo": _display_path(args.input),
                    "resumen": summarize_products(productos),
                    "productos": productos,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(render_text_report(productos, args.input))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
