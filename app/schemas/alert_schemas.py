from pydantic import BaseModel, constr, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AlertStatus(str, Enum):
    CREADO = "creado"
    STOCK_MINIMO = "stock_minimo"
    STOCK_BAJO = "stock_bajo"

class AlertFilter(BaseModel):
    estado: Optional[AlertStatus] = None
    id_sucursal: Optional[int] = None
    mes: Optional[str] = None

    @validator('mes')
    def validate_mes(cls, v):
        if v is None:
            return v
            
        import re
        # Patrón para validar YYYY-MM donde YYYY es 2024, 2025 o 2026 y MM es 01-12
        if not re.match(r"^(202[4-6])-(0[1-9]|1[0-2])$", v):
            raise ValueError(
                "Formato inválido para mes. Debe ser YYYY-MM donde:\n"
                "- YYYY debe ser 2024, 2025 o 2026\n"
                "- MM debe ser 01-12 (con cero inicial para meses 1-9)"
            )
            
        try:
            year, month = v.split('-')
            # Validación adicional del año
            if year not in ['2024', '2025', '2026']:
                raise ValueError("Año debe ser 2024, 2025 o 2026")
            
            # Validación adicional del mes
            month_int = int(month)
            if not (1 <= month_int <= 12):
                raise ValueError("Mes debe estar entre 01 y 12")
                
            return v
        except ValueError as e:
            raise ValueError(f"Error en el formato de fecha: {str(e)}")

class AlertUpdate(BaseModel):
    estado: AlertStatus

class Alert(BaseModel):
    id_alerta: int
    id_inventario: int
    fecha_alerta: datetime
    cantidad_actual: float
    estado: str
    observacion: Optional[str] = None
    
    # Información adicional
    nombre_producto: str
    codigo_producto: str
    nombre_sucursal: str
    nombre_proveedor: str

    class Config:
        from_attributes = True

class AlertHistoryResponse(BaseModel):
    alertas: List[Alert]
    total: int
    pagina_actual: int
    total_paginas: int
    elementos_por_pagina: int