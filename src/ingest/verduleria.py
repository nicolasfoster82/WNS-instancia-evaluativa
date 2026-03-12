from __future__ import annotations


def build_product_payload(productos: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "categoria": producto["categoria"],
            "subcategoria": producto["subcategoria"],
            "nombre": producto["nombre"],
            "precio_kg_ars": producto["precio_kg_ars"],
            "es_estacional": producto["es_estacional"],
        }
        for producto in productos
    ]
