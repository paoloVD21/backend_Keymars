from sqlalchemy.orm import Session
from app.models.inventory_models import Marca
from typing import List

class BrandService:
    @staticmethod
    def get_active_brands(db: Session) -> List[Marca]:
        """
        Obtiene todas las marcas activas
        """
        return db.query(Marca).filter(Marca.activo == True).order_by(Marca.nombre).all()