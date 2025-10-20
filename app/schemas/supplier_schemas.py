from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SupplierBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    contacto: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id_proveedor: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class SupplierList(BaseModel):
    total: int
    proveedores: List[SupplierResponse]

    class Config:
        from_attributes = True