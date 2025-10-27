from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.movement_service import MovementService
from app.schemas import movement_schemas
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.models import Usuario
from datetime import datetime
from typing import List

class MovementController:
    @staticmethod
    async def get_movements_by_date(
        date: datetime,
        db: Session = Depends(get_db)
    ) -> List[movement_schemas.MovementListResponse]:
        """
        Obtiene los movimientos realizados en una fecha específica
        """
        service = MovementService(db)
        try:
            return service.get_movements_by_date(date)
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