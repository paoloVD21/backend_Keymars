from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    codigo_producto: str = Field(..., min_length=3, max_length=50)
    nombre: str = Field(..., min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    id_categoria: int
    id_marca: Optional[int] = None
    unidad_medida: str = Field(..., max_length=50)

class ProductCreate(ProductBase):
    id_proveedor: int
    precio: Decimal = Field(..., ge=Decimal('0'))
    stock_minimo: Decimal = Field(default=Decimal('0'))

class ProductUpdate(ProductBase):
    id_proveedor: int
    precio: Decimal = Field(..., ge=Decimal('0'))
    stock_minimo: Decimal = Field(default=Decimal('0'))

class ProductResponse(ProductBase):
    id_producto: int
    activo: bool
    fecha_creacion: datetime
    categoria_nombre: str
    marca_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    stock_actual: Decimal = Field(default=Decimal('0'))
    stock_minimo: Decimal = Field(default=Decimal('0'))
    precio: Decimal = Field(default=Decimal('0'))

    class Config:
        from_attributes = True

class ProductList(BaseModel):
    total: int
    productos: List[ProductResponse]

    class Config:
        from_attributes = True

class ProductModal(BaseModel):
    id_producto: int
    nombre: str
    codigo_producto: str

    class Config:
        from_attributes = True