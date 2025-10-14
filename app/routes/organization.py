from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.organization_controller import OrganizationController
from app.schemas.organization_schemas import RolResponse, SucursalResponse
from app.utils.auth import verify_token
from app.config.database import get_db
from typing import List

router = APIRouter(
    prefix="/organization",
    tags=["organization"]
)

def get_controller(db: Session = Depends(get_db)) -> OrganizationController:
    return OrganizationController(db)

@router.get("/roles", response_model=List[RolResponse])
def get_roles(
    controller: OrganizationController = Depends(get_controller),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista de roles activos
    """
    return controller.get_roles()

@router.get("/sucursales", response_model=List[SucursalResponse])
def get_sucursales(
    controller: OrganizationController = Depends(get_controller),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista de sucursales activas
    """
    return controller.get_sucursales()