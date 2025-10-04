from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import AuthService
from app.schemas import auth_schemas
from app.config.database import get_db

class AuthController:
    @staticmethod
    async def login(form_data: OAuth2PasswordRequestForm, db: Session) -> auth_schemas.TokenResponse:
        """
        Maneja el proceso de inicio de sesión
        
        Args:
            form_data: Datos del formulario de inicio de sesión
            db: Sesión de base de datos
            
        Returns:
            TokenResponse: Token de acceso y datos del usuario
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        user = AuthService.authenticate_user(db, form_data.username, form_data.password)
        session = AuthService.create_user_session(db, user)
        
        # Convertir el modelo SQLAlchemy a un dict para crear el TokenResponse
        return auth_schemas.TokenResponse(
            access_token=str(session.token_sesion),  # Convertir explícitamente a str
            token_type="bearer",
            user=user  # El modelo User ya tiene Config.from_attributes = True en el schema
        )

    @staticmethod
    async def logout(token: str, db: Session) -> dict:
        """
        Maneja el proceso de cierre de sesión
        
        Args:
            token: Token de sesión a invalidar
            db: Sesión de base de datos
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si hay un error al cerrar la sesión
        """
        if AuthService.logout_user(db, token):
            return {"message": "Sesión cerrada exitosamente"}
        raise HTTPException(status_code=400, detail="Error al cerrar sesión")

    @staticmethod
    async def get_session_info(token: str, db: Session) -> auth_schemas.SessionInfo:
        """
        Obtiene la información de la sesión actual
        
        Args:
            token: Token de sesión actual
            db: Sesión de base de datos
            
        Returns:
            SessionInfo: Información de la sesión actual
            
        Raises:
            HTTPException: Si la sesión es inválida o ha expirado
        """
        return AuthService.get_current_session(db, token)