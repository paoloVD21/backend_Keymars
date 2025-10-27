from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class MovementDetailBase(BaseModel):
    id_producto: int
    id_ubicacion: int
    cantidad: int = Field(..., gt=0)  # La cantidad debe ser mayor que 0

class MovementCreate(BaseModel):
    id_motivo: int  # El motivo se debe enviar desde el frontend (ejemplo: Compra, Devolución, etc.)
    id_sucursal: int
    id_proveedor: Optional[int] = None  # Opcional, requerido solo para ingresos
    observacion: str = Field(..., description="Observaciones del movimiento")
    detalles: List[MovementDetailBase]
    id_usuario: int = Field(..., description="ID del usuario que realiza el movimiento")

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
    precio_unitario: Decimal
    precio_total: Decimal

    class Config:
        from_attributes = True

# Configuración común para los modelos de movimiento
common_config = {"from_attributes": True}

class MovementListResponse(BaseModel):
    """Respuesta resumida para listar movimientos"""
    id_movimiento: int
    motivo_nombre: str
    cantidad_total: int
    proveedor_nombre: Optional[str]
    nombre_usuario: str
    sucursal_nombre: str

    class Config:
        from_attributes = True

class MovementDetailedResponse(BaseModel):
    """Respuesta detallada de un movimiento"""
    id_movimiento: int
    motivo_nombre: str
    cantidad_total: int
    proveedor_nombre: Optional[str]
    nombre_usuario: str
    sucursal_nombre: str
    detalles: List[MovementDetailResponse]

    class Config:
        from_attributes = True