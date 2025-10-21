from sqlalchemy.orm import Session
from app.services.brand_service import BrandService
from app.schemas import brand_schemas
from typing import List

class BrandController:
    def __init__(self, db: Session):
        self.db = db
        self.service = BrandService()

    def get_active_brands(self) -> List[brand_schemas.BrandResponse]:
        """
        Obtiene la lista de marcas activas (solo id y nombre)
        """
        brands = self.service.get_active_brands(self.db)
        return [brand_schemas.BrandResponse.model_validate({
            'id_marca': brand.id_marca,
            'nombre': brand.nombre
        }) for brand in brands]