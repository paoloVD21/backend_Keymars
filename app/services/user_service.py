from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.auth_models import Usuario
from app.schemas import user_schemas
from app.utils.auth import get_password_hash
from typing import List, Tuple, Optional, Sequence

class UserService:
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> Tuple[List[Usuario], int]:
        """
        Obtiene la lista de usuarios con filtros opcionales
        """
        query = db.query(Usuario)
        
        # Aplicar filtro de búsqueda si existe
        if search:
            search_filter = or_(
                Usuario.nombre.ilike(f"%{search}%"),
                Usuario.apellido.ilike(f"%{search}%"),
                Usuario.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            
        # Aplicar filtro de estado si existe
        if activo is not None:
            query = query.filter(Usuario.activo == activo)
            
        # Obtener total de registros
        total = query.count()
        
        # Aplicar paginación
        usuarios = query.offset(skip).limit(limit).all()
        
        return usuarios, total

    @staticmethod
    def create_user(db: Session, user_data: user_schemas.UserCreate) -> Usuario:
        """
        Crea un nuevo usuario
        """
        # Verificar si el email ya existe
        if db.query(Usuario).filter(Usuario.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
            
        # Verificar si el supervisor existe
        if user_data.id_supervisor:
            supervisor = db.query(Usuario).filter(
                Usuario.id_usuario == user_data.id_supervisor
            ).first()
            if not supervisor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El supervisor especificado no existe"
                )
        
        # Crear el hash de la contraseña
        hashed_password = get_password_hash(user_data.password)
        
        # Crear el usuario
        db_user = Usuario(
            **user_data.model_dump(exclude={'password'}),
            password_hash=hashed_password,
            activo=True
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear el usuario"
            ) from e

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        user_data: user_schemas.UserUpdate
    ) -> Usuario:
        """
        Actualiza los datos de un usuario
        """
        # Buscar el usuario
        db_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
            
        # Verificar si el nuevo email ya existe
        if user_data.email and user_data.email != db_user.email:
            if db.query(Usuario).filter(Usuario.email == user_data.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
                
        # Actualizar contraseña si se proporciona
        update_data = user_data.model_dump(exclude_unset=True)
        if 'password' in update_data:
            update_data['password_hash'] = get_password_hash(update_data.pop('password'))
            
        # Verificar supervisor si se proporciona
        if 'id_supervisor' in update_data and update_data['id_supervisor']:
            if update_data['id_supervisor'] == user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Un usuario no puede ser su propio supervisor"
                )
            supervisor = db.query(Usuario).filter(
                Usuario.id_usuario == update_data['id_supervisor']
            ).first()
            if not supervisor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El supervisor especificado no existe"
                )
        
        try:
            # Actualizar los datos
            for key, value in update_data.items():
                setattr(db_user, key, value)
            
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el usuario"
            ) from e

    @staticmethod
    def toggle_user_status(db: Session, user_id: int, active: bool) -> Usuario:
        """
        Activa o desactiva un usuario
        """
        # Buscar el usuario
        db_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
            
        try:
            # Actualizar estado usando update()
            db.query(Usuario).filter(
                Usuario.id_usuario == user_id
            ).update(
                {"activo": active},
                synchronize_session='fetch'
            )
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el estado del usuario"
            ) from e