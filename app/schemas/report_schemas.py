from pydantic import BaseModel
from enum import Enum
from typing import Optional

class ReportType(str, Enum):
    INVENTORY_SUMMARY = "resumen_inventario"
    LOW_STOCK = "stock_bajo"
    MOVEMENT_SUMMARY = "mayores_movimientos"

class Period(str, Enum):
    LAST_MONTH = "ultimo_mes"
    LAST_QUARTER = "ultimo_trimestre"
    LAST_YEAR = "ultimo_anio"