from __future__ import annotations


def build_recipe_payload(recetas: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "nombre": receta["nombre"],
            "instrucciones": receta["instrucciones"],
            "ingredientes": [
                {
                    "nombre_producto": ingrediente["nombre_producto"],
                    "cantidad_gramos": ingrediente["cantidad_gramos"],
                }
                for ingrediente in receta["ingredientes"]
            ],
        }
        for receta in recetas
    ]
