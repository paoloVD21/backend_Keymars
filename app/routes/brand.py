from fastapi import APIRouter, Depends
from app.controllers.brand_controller import BrandController
from app.schemas import brand_schemas
from typing import List
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import verify_token

router = APIRouter(
    prefix="/api/brands",
    tags=["brands"]
)

@router.get("/listarMarcas", response_model=List[brand_schemas.BrandResponse])
def get_marcas_activas(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista de marcas activas para selector/modal
    """
    controller = BrandController(db)
    return controller.get_active_brands()