from fastapi import APIRouter, Depends, HTTPException
from app.controllers.movement_controller import MovementController
from app.controllers.movement_reason_controller import MovementReasonController
from app.schemas import movement_schemas, movement_reason_schemas
from app.utils.auth import get_current_active_user
from app.models import Usuario
from typing import List
from sqlalchemy.orm import Session
from app.config.database import get_db

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

@router.post(
    "/registrarIngreso",
    response_model=movement_schemas.MovementResponse,
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
        print("\n--------- INICIO REGISTRO DE INGRESO ---------")
        print("Datos recibidos:", movement_data.model_dump())
        
        # Llamar al controlador directamente con los datos recibidos
        result = await MovementController.create_entry_movement(
            movement_data=movement_data,
            current_user=current_user,
            db=db
        )
        print("Movimiento creado exitosamente")
        return result
    except HTTPException as e:
        print(f"Error HTTP en registro de ingreso: {str(e)}")
        raise
    except Exception as e:
        print(f"Error inesperado en registro de ingreso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        print("--------- FIN REGISTRO DE INGRESO ---------")