from fastapi import APIRouter, Depends, HTTPException
from app.controllers.movement_controller import MovementController
from app.controllers.movement_reason_controller import MovementReasonController
from app.schemas import movement_schemas, movement_reason_schemas
from app.utils.auth import get_current_active_user
from app.models import Usuario
from typing import List
from sqlalchemy.orm import Session
from app.config.database import get_db
from datetime import datetime

router = APIRouter(
    prefix="/api/movements",
    tags=["movements"]
)

@router.get(
    "/motivos/entrada",
    response_model=List[movement_reason_schemas.MovementReasonResponse],
    summary="Obtener motivos de entrada"
)
async def get_entry_reasons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene todos los motivos de movimiento activos de tipo ENTRADA
    """
    return await MovementReasonController.get_movement_reasons_by_type(
        tipo_movimiento="ENTRADA",
        db=db
    )

@router.get(
    "/motivos/salida",
    response_model=List[movement_reason_schemas.MovementReasonResponse],
    summary="Obtener motivos de salida"
)
async def get_exit_reasons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene todos los motivos de movimiento activos de tipo SALIDA
    """
    return await MovementReasonController.get_movement_reasons_by_type(
        tipo_movimiento="SALIDA",
        db=db
    )

@router.get(
    "/historial/{fecha}",
    response_model=List[movement_schemas.MovementListResponse],
    summary="Obtener historial de movimientos por fecha"
)
async def get_movements_by_date(
    fecha: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene todos los movimientos realizados en una fecha específica
    
    - **fecha**: La fecha en formato 'YYYY-MM-DD'
    """
    try:
        date = datetime.strptime(fecha, "%Y-%m-%d")
        return await MovementController.get_movements_by_date(date, db)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

@router.post(
    "/registrarIngreso",
    response_model=movement_schemas.MovementDetailedResponse,
    summary="Registrar ingreso de productos"
)
async def create_entry_movement(
    movement_data: movement_schemas.MovementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Registra un nuevo ingreso de productos al inventario.

    - **id_motivo**: ID del motivo de ingreso (seleccionado del frontend)
    - **id_sucursal**: ID de la sucursal donde se realiza el ingreso
    - **id_proveedor**: ID del proveedor que realiza la entrega
    - **observacion**: Observaciones adicionales del movimiento
    - **detalles**: Lista de productos a ingresar con sus cantidades y ubicaciones
    """
    try:
        # Llamar al controlador directamente con los datos recibidos
        result = await MovementController.create_entry_movement(
            movement_data=movement_data,
            current_user=current_user,
            db=db
        )
        return result
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")