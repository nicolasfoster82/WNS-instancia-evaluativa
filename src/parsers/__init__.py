from src.parsers.carnes_pescados import (
    DEFAULT_INPUT as CARNES_PESCADOS_INPUT,
    parse_carnes_pescados,
    summarize_products as summarize_carnes_pescados,
)
from src.parsers.recetas import (
    DEFAULT_INPUT as RECETAS_INPUT,
    parse_recetas,
    summarize_recetas,
)
from src.parsers.verduleria import (
    DEFAULT_INPUT as VERDULERIA_INPUT,
    parse_verduleria,
    summarize_products as summarize_verduleria,
)

__all__ = [
    "CARNES_PESCADOS_INPUT",
    "RECETAS_INPUT",
    "VERDULERIA_INPUT",
    "parse_carnes_pescados",
    "parse_recetas",
    "parse_verduleria",
    "summarize_carnes_pescados",
    "summarize_recetas",
    "summarize_verduleria",
]
