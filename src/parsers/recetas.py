from __future__ import annotations

import re
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "inputs" / "Recetas.md"

INGREDIENT_HEADINGS = {"lista de ingredientes", "ingredientes", "lista"}
INSTRUCTION_HEADINGS = {"instrucciones", "preparacion"}
LIST_PREFIX = r"(?:(?:[-*])|(?:\d+\.)|(?:[a-zA-Z]\.))?\s*"
QUANTITY_FIRST_PATTERN = re.compile(
    rf"^{LIST_PREFIX}(?P<cantidad>\d+(?:[.,]\d+)?)\s*(?P<unidad>kg|g)\s+de\s+(?P<nombre>.+)$",
    re.IGNORECASE,
)
NAME_FIRST_PATTERN = re.compile(
    rf"^{LIST_PREFIX}(?P<nombre>.+?)\s*:\s*(?P<cantidad>\d+(?:[.,]\d+)?)\s*(?P<unidad>kg|g)$",
    re.IGNORECASE,
)


def _normalize_heading(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.lower().split())


def _read_markdown(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _parse_quantity_to_grams(quantity_raw: str, unit_raw: str) -> int:
    quantity = float(quantity_raw.replace(",", "."))
    factor = 1000 if unit_raw.lower() == "kg" else 1
    return int(round(quantity * factor))


def _parse_ingredient_line(line: str) -> dict[str, object] | None:
    for pattern in (QUANTITY_FIRST_PATTERN, NAME_FIRST_PATTERN):
        match = pattern.match(line)
        if not match:
            continue

        return {
            "nombre_producto": match.group("nombre").strip(),
            "cantidad_gramos": _parse_quantity_to_grams(
                match.group("cantidad"),
                match.group("unidad"),
            ),
        }

    return None


def _parse_recipe_block(lines: list[str]) -> dict[str, object] | None:
    if not lines:
        return None

    nombre = lines[0].removeprefix("#").strip()
    ingredientes: list[dict[str, object]] = []
    instrucciones: list[str] = []
    section = None

    for raw_line in lines[1:]:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#"):
            heading = _normalize_heading(line.lstrip("#").strip())
            if heading in INGREDIENT_HEADINGS:
                section = "ingredients"
            elif heading in INSTRUCTION_HEADINGS:
                section = "instructions"
            else:
                section = None
            continue

        if section == "ingredients":
            ingredient = _parse_ingredient_line(line)
            if ingredient:
                ingredientes.append(ingredient)
        elif section == "instructions":
            instrucciones.append(line)

    if not ingredientes:
        return None

    return {
        "nombre": nombre,
        "instrucciones": " ".join(instrucciones),
        "ingredientes": ingredientes,
    }


def parse_recetas(file_path: Path = DEFAULT_INPUT) -> list[dict[str, object]]:
    recetas: list[dict[str, object]] = []
    current_block: list[str] = []

    for line in _read_markdown(file_path).splitlines():
        if line.startswith("# "):
            if current_block:
                receta = _parse_recipe_block(current_block)
                if receta:
                    recetas.append(receta)
            current_block = [line]
        elif current_block:
            current_block.append(line)

    if current_block:
        receta = _parse_recipe_block(current_block)
        if receta:
            recetas.append(receta)

    return recetas


def summarize_recetas(recetas: list[dict[str, object]]) -> dict[str, object]:
    return {
        "total_recetas": len(recetas),
        "total_ingredientes": sum(len(receta["ingredientes"]) for receta in recetas),
        "ingredientes_por_receta": {
            str(receta["nombre"]): len(receta["ingredientes"]) for receta in recetas
        },
    }
