from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class MovementDetailBase(BaseModel):
    id_producto: int
    id_ubicacion: int
    cantidad: int = Field(..., gt=0)  # La cantidad debe ser mayor que 0

class MovementCreate(BaseModel):
    id_motivo: int = Field(1)  # Valor por defecto 1 para Compra
    id_sucursal: int
    observacion: str = Field(..., description="Formato: 'Fecha: YYYY-MM-DD - Proveedor: NombreProveedor'")
    detalles: List[MovementDetailBase]

    @validator('detalles')
    def validate_details(cls, v):
        if not v:
            raise ValueError('La lista de productos no puede estar vacía')
        return v

class MovementDetailResponse(BaseModel):
    id_movimiento_detalle: int
    nombre_producto: str
    codigo_producto: str
    ubicacion_nombre: str
    cantidad: int
    id_producto: int
    id_ubicacion: int

    class Config:
        from_attributes = True

class MovementResponse(BaseModel):
    id_movimiento: int
    tipo_movimiento: str
    numero_documento: Optional[str]
    observacion: Optional[str]
    fecha_movimiento: datetime
    nombre_usuario: str
    motivo_nombre: str
    sucursal_nombre: str
    detalles: List[MovementDetailResponse]

    class Config:
        from_attributes = True