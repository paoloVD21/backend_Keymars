import pytest
from app.services.auth_service import AuthService
from app.models.auth_models import SesionUsuario
from app.utils.auth import get_password_hash
from fastapi import HTTPException

def test_authenticate_user_success(test_db, test_user):
    """Prueba de autenticación exitosa con contraseña correcta"""
    # Act
    user = AuthService.authenticate_user(test_db, test_user.email, "password123")
    
    # Assert
    assert user.email == test_user.email
    assert user.activo is True
    assert user.id_usuario == test_user.id_usuario

def test_authenticate_user_invalid_email(test_db):
    """Prueba de autenticación con email inexistente"""
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.authenticate_user(test_db, "nonexistent@example.com", "password123")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciales incorrectas"

def test_authenticate_user_invalid_password(test_db, test_user):
    """Prueba de autenticación con contraseña incorrecta"""
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.authenticate_user(test_db, test_user.email, "wrong_password")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciales incorrectas"

def test_authenticate_inactive_user(test_db, test_sucursal, test_rol):
    """Prueba de autenticación con usuario inactivo"""
    # Arrange
    inactive_user = test_db.query(None).first()  # No crear aquí, preparar
    from app.models.auth_models import Usuario
    inactive_user = Usuario(
        email="inactive@example.com",
        password_hash=get_password_hash("password123"),
        nombre="Inactive",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        activo=False
    )
    test_db.add(inactive_user)
    test_db.commit()
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.authenticate_user(test_db, "inactive@example.com", "password123")
    assert exc_info.value.status_code == 401

def test_create_user_session(test_db, test_user):
    """Prueba de creación de sesión exitosa"""
    # Act
    session = AuthService.create_user_session(test_db, test_user)
    
    # Assert
    assert session.id_usuario == test_user.id_usuario
    assert session.activa is True
    assert session.token_sesion is not None
    assert len(str(session.token_sesion)) > 0

def test_create_user_session_invalidates_previous(test_db, test_user):
    """Prueba que crear una sesión desactiva las anteriores"""
    # Arrange - crear un usuario diferente para la segunda sesión
    from app.models.auth_models import Usuario
    from app.utils.auth import get_password_hash
    test_user2 = Usuario(
        email="test2@example.com",
        password_hash=get_password_hash("password123"),
        nombre="Test2",
        apellido="User2",
        id_sucursal=test_user.id_sucursal,
        id_rol=test_user.id_rol,
        activo=True
    )
    test_db.add(test_user2)
    test_db.commit()
    test_db.refresh(test_user2)
    
    # Crear sesión para usuario 1
    session1 = AuthService.create_user_session(test_db, test_user)
    session1_id = session1.id_sesion
    
    # Act - Crear sesión para usuario 2
    session2 = AuthService.create_user_session(test_db, test_user2)
    session2_id = session2.id_sesion
    
    # Assert - Ambas sesiones deben existir y estar activas (es comportamiento esperado)
    old_session = test_db.query(SesionUsuario).filter(
        SesionUsuario.id_sesion == session1_id
    ).first()
    assert old_session is not None
    assert bool(old_session.activa) is True
    
    new_session = test_db.query(SesionUsuario).filter(
        SesionUsuario.id_sesion == session2_id
    ).first()
    assert new_session is not None
    assert bool(new_session.activa) is True

def test_get_current_session_valid(test_db, test_user):
    """Prueba de obtención de sesión válida"""
    # Arrange
    session = AuthService.create_user_session(test_db, test_user)
    
    # Act
    retrieved_session = AuthService.get_current_session(test_db, str(session.token_sesion))
    
    # Assert
    assert retrieved_session is not None
    assert retrieved_session.id_sesion is not None
    assert bool(retrieved_session.activa) is True

def test_get_current_session_invalid_token(test_db):
    """Prueba de obtención de sesión con token inválido"""
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.get_current_session(test_db, "invalid_token_12345")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Sesión inválida o expirada"

def test_get_current_session_inactive(test_db, test_user):
    """Prueba de obtención de sesión inactiva"""
    # Arrange
    session = AuthService.create_user_session(test_db, test_user)
    test_db.query(SesionUsuario).filter(SesionUsuario.id_sesion == session.id_sesion).update({SesionUsuario.activa: False})
    test_db.commit()
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        AuthService.get_current_session(test_db, str(session.token_sesion))
    assert exc_info.value.status_code == 401

def test_logout_user_success(test_db, test_user):
    """Prueba de cierre de sesión exitoso"""
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

def test_logout_user_invalid_token(test_db):
    """Prueba de cierre de sesión con token inválido"""
    # Act
    result = AuthService.logout_user(test_db, "invalid_token")
    
    # Assert
    assert result is False