import pytest
from app.utils.auth import get_password_hash

def test_login_endpoint_invalid_password(client, test_user):
    """Prueba del endpoint de login con contraseña incorrecta"""
    # Act
    response = client.post("/api/auth/login", data={
        "username": test_user.email,
        "password": "wrong_password"
    })
    
    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"

def test_logout_endpoint_no_token(client):
    """Prueba del endpoint de logout sin token"""
    # Act
    response = client.post("/api/auth/logout")
    
    # Assert
    assert response.status_code == 401  # Unauthorized

def test_get_session_info_no_token(client):
    """Prueba del endpoint de información de sesión sin token"""
    # Act
    response = client.get("/api/auth/session")
    
    # Assert
    assert response.status_code == 401  # Unauthorized