import pytest
from app.services.auth_service import AuthService
from app.models.auth_models import SesionUsuario
from fastapi import HTTPException

def test_authenticate_user_success(test_db, test_user):
    """Prueba de autenticación exitosa"""
    # Act
    user = AuthService.authenticate_user(test_db, test_user.email, "password123")
    
    # Assert
    assert user.email == test_user.email
    assert user.activo is True

def test_authenticate_user_invalid_credentials(test_db, test_user):
    """Prueba de autenticación con credenciales inválidas"""
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.authenticate_user(test_db, test_user.email, "wrong_password")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciales incorrectas"

def test_create_user_session(test_db, test_user):
    """Prueba de creación de sesión"""
    # Act
    session = AuthService.create_user_session(test_db, test_user)
    
    # Assert
    assert session.id_usuario == test_user.id_usuario
    assert session.activa is True
    assert session.token_sesion is not None

def test_logout_user(test_db, test_user):
    """Prueba de cierre de sesión"""
    # Arrange
    session = AuthService.create_user_session(test_db, test_user)
    
    # Act
    result = AuthService.logout_user(test_db, str(session.token_sesion))
    
    # Assert
    assert result is True
    updated_session = test_db.query(SesionUsuario).filter_by(
        token_sesion=session.token_sesion
    ).first()
    assert updated_session.activa is False

def test_get_current_session_invalid(test_db):
    """Prueba de obtención de sesión inválida"""
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.get_current_session(test_db, "invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Sesión inválida o expirada"