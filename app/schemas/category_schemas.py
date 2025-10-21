from pydantic import BaseModel, Field

class CategoryResponse(BaseModel):
    id_categoria: int
    nombre: str
    activo: bool = True

    class Config:
        from_attributes = True