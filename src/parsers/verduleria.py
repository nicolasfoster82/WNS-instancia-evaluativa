from __future__ import annotations

import re
from pathlib import Path

import pdfplumber as pdf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "inputs" / "verduleria.pdf"

CATEGORY = "Verdulería"
PRICE_PATTERN = re.compile(r"^([A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+)\s+\$([\d.]+(?:,\d+)?)$")
TYPE_SUFFIX = " por kg"


def _clean_and_convert_price(value: str) -> float | None:
    cleaned = value.replace("$", "").replace("ARS", "").replace(" ", "")
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", cleaned):
        cleaned = cleaned.replace(".", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return None


def _build_product(name: str, price_raw: str) -> dict[str, object]:
    return {
        "categoria": CATEGORY,
        "subcategoria": None,
        "nombre": name.strip(),
        "precio_kg_ars": _clean_and_convert_price(price_raw),
        "es_estacional": False,
    }


def parse_verduleria(file_path: Path = DEFAULT_INPUT) -> list[dict[str, object]]:
    productos: list[dict[str, object]] = []

    with pdf.open(file_path) as pdf_file:
        for page in pdf_file.pages:
            lines = [line.strip() for line in (page.extract_text() or "").splitlines() if line.strip()]
            index = 0

            while index < len(lines):
                match = PRICE_PATTERN.match(lines[index])
                if not match:
                    index += 1
                    continue

                producto = _build_product(match.group(1), match.group(2))
                index += 1

                while index < len(lines) and not PRICE_PATTERN.match(lines[index]):
                    detail = lines[index]
                    if detail == "De estación":
                        producto["es_estacional"] = True
                    elif detail.endswith(TYPE_SUFFIX):
                        producto["subcategoria"] = detail.removesuffix(TYPE_SUFFIX)
                    index += 1

                if producto["precio_kg_ars"] is not None and producto["subcategoria"]:
                    productos.append(producto)

    return productos


def summarize_products(productos: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for producto in productos:
        categoria = str(producto["categoria"])
        subcategoria = str(producto["subcategoria"])
        summary.setdefault(categoria, {})
        summary[categoria][subcategoria] = summary[categoria].get(subcategoria, 0) + 1
    return summary
