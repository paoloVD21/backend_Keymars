from fastapi import APIRouter, Depends
from app.controllers.movement_controller import MovementController
from app.schemas import movement_schemas
from app.utils.auth import get_current_active_user
from app.models import Usuario

router = APIRouter(
    prefix="/api/movements",
    tags=["movements"]
)

@router.post(
    "/registrarIngreso",
    response_model=movement_schemas.MovementResponse,
    summary="Registrar ingreso de productos"
)
async def create_entry_movement(
    movement_data: movement_schemas.MovementCreate,
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Registra un nuevo ingreso de productos al inventario.

    - **id_motivo**: ID del motivo de ingreso
    - **id_sucursal**: ID de la sucursal donde se realiza el ingreso
    - **numero_documento**: Número de documento (opcional)
    - **observacion**: Observaciones adicionales (opcional)
    - **detalles**: Lista de productos a ingresar con sus cantidades y ubicaciones
    """
    return await MovementController.create_entry_movement(
        movement_data=movement_data,
        current_user=current_user
    )