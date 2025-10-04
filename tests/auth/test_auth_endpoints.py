import pytest
from fastapi.testclient import TestClient
from app.utils.auth import get_password_hash

@pytest.mark.asyncio
async def test_login_endpoint_success(client, test_db, test_user):
    """Prueba del endpoint de login exitoso"""
    # Arrange
    test_user.password_hash = get_password_hash("password123")
    test_db.commit()
    
    # Act
    response = client.post("/api/auth/login", data={
        "username": test_user.email,
        "password": "password123"
    })
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

@pytest.mark.asyncio
async def test_login_endpoint_invalid_credentials(client, test_user):
    """Prueba del endpoint de login con credenciales inválidas"""
    # Act
    response = client.post("/api/auth/login", data={
        "username": test_user.email,
        "password": "wrong_password"
    })
    
    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"

@pytest.mark.asyncio
async def test_logout_endpoint(client, test_db, test_user):
    """Prueba del endpoint de logout"""
    # Arrange - Primero hacer login
    test_user.password_hash = get_password_hash("password123")
    test_db.commit()
    
    login_response = client.post("/api/auth/login", data={
        "username": test_user.email,
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Act
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Sesión cerrada exitosamente"

@pytest.mark.asyncio
async def test_get_session_info(client, test_db, test_user):
    """Prueba del endpoint de información de sesión"""
    # Arrange - Primero hacer login
    test_user.password_hash = get_password_hash("password123")
    test_db.commit()
    
    login_response = client.post("/api/auth/login", data={
        "username": test_user.email,
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Act
    response = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert
    assert response.status_code == 200
    session_info = response.json()
    assert "id_sesion" in session_info
    assert session_info["activa"] is True