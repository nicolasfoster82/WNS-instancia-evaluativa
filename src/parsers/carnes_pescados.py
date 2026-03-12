from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]


DEFAULT_INPUT = PROJECT_ROOT / "inputs" / "Carnes y Pescados.xlsx"

MEAT_NAME_COL = 2
MEAT_PRICE_COL = 3
FISH_NAME_COL = 5
FISH_PRICE_COL = 6

MEAT_CATEGORY = "Carnicería"
FISH_CATEGORY = "Pescadería"
FISH_SUBCATEGORY = "General"
MEAT_SUBCATEGORIES = {"Carne Vacuna", "Carne de Cerdo", "Pollo"}
IGNORED_NAMES = {"Carnicería", "Pescadería", "Corte", "Precio (ARS/kg)", "Tipo"}


def _read_excel(file_path: Path) -> "pd.DataFrame":
    return pd.read_excel(file_path, header=None, engine="openpyxl")


def _cell_to_text(value: object) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def _clean_and_convert_price(value: object) -> float | None:
    text = _cell_to_text(value)
    if not text:
        return None

    cleaned = text.replace("ARS", "").replace("$", "").replace(" ", "")
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", cleaned):
        cleaned = cleaned.replace(".", "")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+", cleaned):
        cleaned = cleaned.replace(",", "")
    elif "." in cleaned and "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return None


def _build_product(categoria: str, subcategoria: str | None, nombre_raw: object, precio_raw: object):
    nombre = _cell_to_text(nombre_raw)
    if not nombre or nombre in IGNORED_NAMES or not subcategoria:
        return None

    precio = _clean_and_convert_price(precio_raw)
    if precio is None:
        return None

    return {
        "categoria": categoria,
        "subcategoria": subcategoria,
        "nombre": nombre,
        "precio_kg_ars": precio,
    }


def parse_carnes_pescados(file_path: Path = DEFAULT_INPUT) -> list[dict[str, object]]:
    df = _read_excel(file_path)
    meat_products: list[dict[str, object]] = []
    fish_products: list[dict[str, object]] = []
    current_meat_subcategory = None

    for _, row in df.iterrows():
        meat_name = _cell_to_text(row.iloc[MEAT_NAME_COL])
        if meat_name in MEAT_SUBCATEGORIES:
            current_meat_subcategory = meat_name
        else:
            meat_product = _build_product(
                MEAT_CATEGORY,
                current_meat_subcategory,
                row.iloc[MEAT_NAME_COL],
                row.iloc[MEAT_PRICE_COL],
            )
            if meat_product:
                meat_products.append(meat_product)

        fish_product = _build_product(
            FISH_CATEGORY,
            FISH_SUBCATEGORY,
            row.iloc[FISH_NAME_COL],
            row.iloc[FISH_PRICE_COL],
        )
        if fish_product:
            fish_products.append(fish_product)

    return meat_products + fish_products


def summarize_products(productos: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for producto in productos:
        categoria = str(producto["categoria"])
        subcategoria = str(producto["subcategoria"])
        summary.setdefault(categoria, {})
        summary[categoria][subcategoria] = summary[categoria].get(subcategoria, 0) + 1
    return summary
