from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: EmailStr
    id_sucursal: int
    id_rol: int
    activo: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class SessionInfo(BaseModel):
    id_sesion: UUID
    fecha_inicio: datetime
    fecha_expiracion: Optional[datetime]
    activa: bool

    class Config:
        from_attributes = True