from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Esquema base solo con campos comunes opcionales
class UserBasePartial(BaseModel):
    id_supervisor: Optional[int] = None

# Esquema para creación con campos requeridos
class UserCreate(UserBasePartial):
    nombre: str
    apellido: str
    email: EmailStr
    id_sucursal: int
    id_rol: int
    password: str

# Esquema para actualización con todos los campos opcionales
class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    id_sucursal: Optional[int] = None
    id_rol: Optional[int] = None
    id_supervisor: Optional[int] = None
    password: Optional[str] = None

# Esquema para respuesta
class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: EmailStr
    id_sucursal: int
    id_rol: int
    id_supervisor: Optional[int]
    fecha_creacion: datetime
    activo: bool

    class Config:
        from_attributes = True

# Esquema para lista de usuarios
class UserList(BaseModel):
    total: int
    usuarios: list[UserResponse]

    # Esquema para cambiar estado de usuario
class ToggleStatusRequest(BaseModel):
    active: bool