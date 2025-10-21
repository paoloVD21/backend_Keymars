from pydantic import BaseModel, Field

class BrandResponse(BaseModel):
    id_marca: int
    nombre: str
    activo: bool = True

    class Config:
        from_attributes = True