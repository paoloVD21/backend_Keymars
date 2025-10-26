from fastapi import APIRouter, Depends
from app.controllers.location_controller import LocationController
from app.schemas import location_schemas
from app.utils.auth import get_current_active_user
from app.models import Usuario
from typing import List
from sqlalchemy.orm import Session
from app.config.database import get_db

router = APIRouter(
    prefix="/api/locations",
    tags=["locations"]
)

@router.get(
    "/sucursal/{branch_id}/ubicaciones",
    response_model=List[location_schemas.LocationResponse],
    summary="Obtener ubicaciones por sucursal"
)
async def get_locations_by_branch(
    branch_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las ubicaciones activas de una sucursal específica.

    - **branch_id**: ID de la sucursal
    
    Retorna una lista de ubicaciones con:
    - id_ubicacion: ID de la ubicación
    - nombre: Nombre de la ubicación
    - codigo_ubicacion: Código único de la ubicación
    - tipo_ubicacion: Tipo de ubicación (ESTANTERIA, REFRIGERADO, SECO, LIQUIDOS, OTROS)
    """
    return await LocationController.get_locations_by_branch(
        branch_id=branch_id,
        current_user=current_user,
        db=db
    )

@router.post(
    "/crearUbicacion",
    response_model=location_schemas.LocationResponse,
    summary="Crear nueva ubicación"
)
async def create_location(
    location_data: location_schemas.LocationCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva ubicación en una sucursal.

    - **nombre**: Nombre de la ubicación (3-100 caracteres)
    - **codigo_ubicacion**: Código único de la ubicación (2-20 caracteres)
    - **tipo_ubicacion**: ESTANTERIA, REFRIGERADO, SECO, LIQUIDOS, OTROS
    - **id_sucursal**: ID de la sucursal a la que pertenece
    """
    return await LocationController.create_location(
        location_data=location_data,
        current_user=current_user,
        db=db
    )