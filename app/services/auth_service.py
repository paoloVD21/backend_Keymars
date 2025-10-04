from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.auth_models import Usuario, SesionUsuario
from app.schemas import auth_schemas
from app.utils.auth import verify_password, create_access_token, get_password_hash
from fastapi import HTTPException
import uuid
import jwt

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Usuario:
        user = db.query(Usuario).filter(
            Usuario.email == email, 
            Usuario.activo.is_(True)
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # Obtener el valor real del hash de la contraseña
        stored_hash = str(user.password_hash) if user.password_hash is not None else ""
        
        if not verify_password(password, stored_hash):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        return user

    @staticmethod
    def create_user_session(db: Session, user: Usuario) -> SesionUsuario:
        # Desactivar sesiones anteriores usando update con synchronize_session
        db.query(SesionUsuario).filter(
            SesionUsuario.id_usuario == user.id_usuario,
            SesionUsuario.activa.is_(True)
        ).update(
            {SesionUsuario.activa: False}, 
            synchronize_session='fetch'
        )
        
        # Crear nueva sesión
        access_token = create_access_token(
            data={"sub": str(user.id_usuario), "email": user.email}
        )
        
        session = SesionUsuario(
            id_usuario=user.id_usuario,
            token_sesion=access_token,
            activa=True,
            fecha_expiracion=datetime.utcnow() + timedelta(days=1)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session

    @staticmethod
    def get_current_session(db: Session, token: str) -> SesionUsuario:
        session = db.query(SesionUsuario).filter(
            SesionUsuario.token_sesion == token,
            SesionUsuario.activa == True,
            SesionUsuario.fecha_expiracion > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
        
        return session

    @staticmethod
    def logout_user(db: Session, token: str) -> bool:
        # Asegurarnos de que el token es un string
        token_str = str(token) if token is not None else ""
        
        result = db.query(SesionUsuario).filter(
            SesionUsuario.token_sesion == token_str,
            SesionUsuario.activa.is_(True)
        ).update(
            {SesionUsuario.activa: False},
            synchronize_session='fetch'
        )
        
        db.commit()
        return result > 0