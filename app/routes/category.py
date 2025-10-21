from fastapi import APIRouter, Depends
from app.controllers.category_controller import CategoryController
from app.schemas import category_schemas
from typing import List
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import verify_token

router = APIRouter(
    prefix="/api/categories",
    tags=["categories"]
)

@router.get("/listarCategorias", response_model=List[category_schemas.CategoryResponse])
def get_categorias_activas(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista de categorías activas para selector/modal
    """
    controller = CategoryController(db)
    return controller.get_active_categories()