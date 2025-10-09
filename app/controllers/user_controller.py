from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schemas import user_schemas
from app.config.database import get_db
from typing import Optional

class UserController:
    @staticmethod
    async def get_users(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        search: Optional[str] = None,
        activo: Optional[bool] = None,
        db: Session = Depends(get_db)
    ) -> user_schemas.UserList:
        """
        Obtiene la lista paginada de usuarios
        """
        usuarios, total = UserService.get_users(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            activo=activo
        )
        # Convertir los usuarios a UserResponse
        user_responses = [user_schemas.UserResponse.model_validate(usuario) for usuario in usuarios]
        return user_schemas.UserList(total=total, usuarios=user_responses)

    @staticmethod
    async def create_user(
        user_data: user_schemas.UserCreate,
        db: Session = Depends(get_db)
    ) -> user_schemas.UserResponse:
        """
        Crea un nuevo usuario
        """
        return UserService.create_user(db=db, user_data=user_data)

    @staticmethod
    async def update_user(
        user_id: int,
        user_data: user_schemas.UserUpdate,
        db: Session = Depends(get_db)
    ) -> user_schemas.UserResponse:
        """
        Actualiza los datos de un usuario
        """
        return UserService.update_user(db=db, user_id=user_id, user_data=user_data)

    @staticmethod
    async def toggle_user_status(
        user_id: int,
        active: bool,
        db: Session = Depends(get_db)
    ) -> user_schemas.UserResponse:
        """
        Activa o desactiva un usuario
        """
        return UserService.toggle_user_status(db=db, user_id=user_id, active=active)