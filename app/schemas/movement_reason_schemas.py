from pydantic import BaseModel

class MovementReasonResponse(BaseModel):
    id_motivo: int
    nombre: str
    tipo_movimiento: str
    activo: bool

    class Config:
        from_attributes = True