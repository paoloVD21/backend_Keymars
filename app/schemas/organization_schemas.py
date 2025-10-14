from pydantic import BaseModel
from typing import List, Optional

class RolResponse(BaseModel):
    id_rol: int
    nombre: str

    class Config:
        from_attributes = True

class RolList(BaseModel):
    roles: List[RolResponse]

class SucursalBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    activo: bool = True

class SucursalResponse(BaseModel):
    id_sucursal: int
    nombre: str

    class Config:
        from_attributes = True

class SucursalList(BaseModel):
    sucursales: List[SucursalResponse]