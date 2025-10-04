from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    cantidad: int
    categoria_id: int

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True