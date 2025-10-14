from fastapi import APIRouter, Depends, Query
from app.controllers.user_controller import UserController
from app.schemas import user_schemas
from typing import Optional
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import verify_token
from app.schemas.user_schemas import ToggleStatusRequest

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.get("/listarUsuarios", response_model=user_schemas.UserList)
async def get_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista paginada de usuarios.
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **search**: Término de búsqueda (nombre, apellido o email)
    - **activo**: Filtrar por estado del usuario
    """
    return await UserController.get_users(
        skip=skip,
        limit=limit,
        search=search,
        activo=activo,
        db=db
    )

@router.post("", response_model=user_schemas.UserResponse)
async def create_user(
    user_data: user_schemas.UserCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Crea un nuevo usuario.
    """
    return await UserController.create_user(user_data=user_data, db=db)

@router.put("/{user_id}", response_model=user_schemas.UserResponse)
async def update_user(
    user_id: int,
    user_data: user_schemas.UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Actualiza los datos de un usuario existente.
    """
    return await UserController.update_user(
        user_id=user_id,
        user_data=user_data,
        db=db
    )

@router.patch("/{user_id}/status", response_model=user_schemas.UserResponse)
async def toggle_user_status(
    user_id: int,
    body: ToggleStatusRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Activa o desactiva un usuario.
    - **active**: True para activar, False para desactivar (enviar en el body)
    """
    return await UserController.toggle_user_status(
        user_id=user_id,
        active=body.active,
        db=db
    )