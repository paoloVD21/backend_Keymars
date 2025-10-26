from pydantic import BaseModel, Field
from typing import List, Optional

class LocationBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    codigo_ubicacion: str = Field(..., min_length=2, max_length=20)
    tipo_ubicacion: str = Field(..., description="ESTANTERIA, REFRIGERADO, SECO, LIQUIDOS, OTROS")
    id_sucursal: int

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id_ubicacion: int
    activo: bool

    class Config:
        from_attributes = True