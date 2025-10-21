from sqlalchemy.orm import Session
from app.models.inventory_models import Categoria
from typing import List

class CategoryService:
    @staticmethod
    def get_active_categories(db: Session) -> List[Categoria]:
        """
        Obtiene todas las categorías activas
        """
        return db.query(Categoria).filter(Categoria.activo == True).order_by(Categoria.nombre).all()