from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.movement_service import MovementService
from app.schemas import movement_schemas
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.models import Usuario

class MovementController:
    @staticmethod
    async def create_entry_movement(
        movement_data: movement_schemas.MovementCreate,
        current_user: Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> movement_schemas.MovementResponse:
        """
        Crea un nuevo movimiento de entrada (ingreso)
        """
        service = MovementService(db)
        # Obtener el ID del usuario
        try:
            if isinstance(current_user, dict):
                user_id = int(current_user.get('id_usuario', 0))
            else:
                # Asegurarse de obtener el valor escalar de la columna SQLAlchemy
                user_id = int(getattr(current_user, 'id_usuario', 0))
                
            if user_id <= 0:
                raise ValueError("ID de usuario inválido")
                
            return service.create_entry_movement(
                movement_data=movement_data,
                user_id=user_id
            )
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="ID de usuario no válido")