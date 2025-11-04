from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.movement_service import MovementService
from app.schemas import movement_schemas
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.models import Usuario
from datetime import datetime
from typing import List, Optional

class MovementController:
    @staticmethod
    async def get_movements_by_date(
        date: datetime,
        db: Session = Depends(get_db),
        tipo_movimiento: Optional[str] = None
    ) -> List[movement_schemas.MovementListResponse]:
        """
        Obtiene los movimientos realizados en una fecha específica
        Si se especifica tipo_movimiento, filtra por INGRESO o EGRESO
        """
        service = MovementService(db)
        try:
            return service.get_movements_by_date(date, tipo_movimiento)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_entry_movement(
        movement_data: movement_schemas.MovementCreate,
        current_user: dict,
        db: Session = Depends(get_db)
    ) -> movement_schemas.MovementDetailedResponse:
        """
        Crea un nuevo movimiento de entrada (ingreso)
        """
        service = MovementService(db)
        try:
            return service.create_entry_movement(movement_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    @staticmethod
    async def create_exit_movement(
        movement_data: movement_schemas.MovementCreate,
        current_user: dict,
        db: Session = Depends(get_db)
    ) -> movement_schemas.MovementDetailedResponse:
        """
        Crea un nuevo movimiento de salida (egreso)
        """
        service = MovementService(db)
        try:
            # Asegurarse de que no se envía proveedor en salidas
            movement_data.id_proveedor = None
            
            return service.create_exit_movement(movement_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def search_products_for_entry(
        id_sucursal: int,
        buscar: str,
        db: Session = Depends(get_db)
    ) -> List[movement_schemas.ProductoEntradaResponse]:
        """
        Busca productos por nombre para registrar entradas
        """
        service = MovementService(db)
        try:
            return service.search_products_for_entry(id_sucursal, buscar)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def search_products_for_movement(
        id_sucursal: int,
        buscar: str,
        db: Session = Depends(get_db)
    ) -> List[movement_schemas.ProductoSearchResponse]:
        """
        Busca productos por nombre o código para un movimiento
        """
        service = MovementService(db)
        try:
            return service.search_products_for_movement(id_sucursal, buscar)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_movement_by_id(
        movement_id: int,
        db: Session = Depends(get_db)
    ) -> movement_schemas.MovementDetailedResponse:
        """
        Obtiene los detalles completos de un movimiento específico
        """
        service = MovementService(db)
        try:
            return service.get_movement_by_id(movement_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))