from sqlalchemy.orm import Session
from app.services.category_service import CategoryService
from app.schemas import category_schemas
from typing import List

class CategoryController:
    def __init__(self, db: Session):
        self.db = db
        self.service = CategoryService()

    def get_active_categories(self) -> List[category_schemas.CategoryResponse]:
        """
        Obtiene la lista de categorías activas (solo id y nombre)
        """
        categories = self.service.get_active_categories(self.db)
        return [category_schemas.CategoryResponse.model_validate({
            'id_categoria': category.id_categoria,
            'nombre': category.nombre
        }) for category in categories]