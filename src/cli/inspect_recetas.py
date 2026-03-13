from __future__ import annotations

import argparse
from pathlib import Path

from src.parsers.recetas import DEFAULT_INPUT, parse_recetas, summarize_recetas


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def render_text_report(recetas: list[dict[str, object]], file_path: Path) -> str:
    summary = summarize_recetas(recetas)
    lines = [
        f"Archivo: {_display_path(file_path)}",
        "Librerias externas de Python: ninguna",
        "",
        "Resumen propuesto para DB:",
        f"- Recetas: {summary['total_recetas']}",
        f"- Ingredientes totales: {summary['total_ingredientes']}",
        "",
        "Recetas normalizadas:",
    ]

    ingredientes_por_receta = summary["ingredientes_por_receta"]
    for receta in recetas:
        lines.append(
            f"- {receta['nombre']} | ingredientes: {ingredientes_por_receta[str(receta['nombre'])]}"
        )
        for ingrediente in receta["ingredientes"]:
            lines.append(
                f"  - {ingrediente['nombre_producto']} | {ingrediente['cantidad_gramos']} g"
            )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and normalize the file inputs/Recetas.md")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the markdown file to inspect.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    recetas = parse_recetas(args.input)
    print(render_text_report(recetas, args.input))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
