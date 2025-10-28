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

@router.post(
    "/registrarSalida",
    response_model=movement_schemas.MovementDetailedResponse,
    summary="Registrar salida de productos"
)
async def create_exit_movement(
    movement_data: movement_schemas.MovementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Registra una nueva salida de productos del inventario.

    - **id_motivo**: ID del motivo de salida (seleccionado del frontend)
    - **id_sucursal**: ID de la sucursal donde se realiza la salida
    - **id_proveedor**: No requerido para salidas (debe ser null)
    - **observacion**: Observaciones adicionales del movimiento
    - **detalles**: Lista de productos a retirar con sus cantidades y ubicaciones
    """
    try:
        result = await MovementController.create_exit_movement(
            movement_data=movement_data,
            current_user=current_user,
            db=db
        )
        return result
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get(
    "/productos/buscar/{id_sucursal}",
    response_model=List[movement_schemas.ProductoSearchResponse],
    summary="Buscar productos para movimiento"
)
async def search_products_for_movement(
    id_sucursal: int,
    buscar: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Busca productos por nombre o código y obtiene su stock en las ubicaciones de la sucursal especificada
    
    - **id_sucursal**: ID de la sucursal donde se quiere buscar los productos
    - **buscar**: Término de búsqueda (parte del nombre o código del producto)

    Retorna una lista de productos que coinciden con la búsqueda, incluyendo:
    - Información básica del producto (ID, nombre, código, precio)
    - Lista de ubicaciones con su stock actual
    """
    try:
        return await MovementController.search_products_for_movement(id_sucursal, buscar, db)
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get(
    "/{movement_id}",
    response_model=movement_schemas.MovementDetailedResponse,
    summary="Obtener detalles de un movimiento"
)
async def get_movement_by_id(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene los detalles completos de un movimiento específico
    
    - **movement_id**: ID del movimiento a consultar
    """
    try:
        return await MovementController.get_movement_by_id(movement_id, db)
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")