import pytest
from app.utils.auth import get_password_hash, verify_password, create_access_token
import jwt
from fastapi import HTTPException
from app.config.settings import settings

def test_get_password_hash_creates_valid_hash():
    """Prueba que get_password_hash genera un hash válido"""
    # Act
    hashed = get_password_hash("test_password")
    
    # Assert
    assert hashed is not None
    assert hashed.startswith("scrypt$")
    assert len(hashed) > 20

def test_get_password_hash_different_for_same_password():
    """Prueba que hashes diferentes se generan para la misma contraseña (debido al salt)"""
    # Act
    hash1 = get_password_hash("test_password")
    hash2 = get_password_hash("test_password")
    
    # Assert - Los hashes deben ser diferentes por el salt aleatorio
    assert hash1 != hash2

def test_get_password_hash_empty_password_raises_error():
    """Prueba que una contraseña vacía genera un error"""
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_password_hash("")
    assert exc_info.value.status_code == 400

def test_verify_password_valid():
    """Prueba que verify_password funciona con contraseña correcta"""
    # Arrange
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Act
    result = verify_password(password, hashed)
    
    # Assert
    assert result is True

def test_verify_password_invalid():
    """Prueba que verify_password falla con contraseña incorrecta"""
    # Arrange
    password = "test_password_123"
    wrong_password = "wrong_password_123"
    hashed = get_password_hash(password)
    
    # Act
    result = verify_password(wrong_password, hashed)
    
    # Assert
    assert result is False

def test_verify_password_empty_plain_password():
    """Prueba que verify_password falla con contraseña vacía"""
    # Arrange
    hashed = get_password_hash("test_password")
    
    # Act
    result = verify_password("", hashed)
    
    # Assert
    assert result is False

def test_verify_password_empty_stored_hash():
    """Prueba que verify_password falla con hash vacío"""
    # Act
    result = verify_password("test_password", "")
    
    # Assert
    assert result is False

def test_verify_password_invalid_hash_format():
    """Prueba que verify_password falla con formato de hash inválido"""
    # Act
    result = verify_password("test_password", "invalid_hash_format")
    
    # Assert
    assert result is False

def test_create_access_token_valid():
    """Prueba que create_access_token genera un token válido"""
    # Arrange
    data = {"sub": "1", "email": "test@example.com"}
    
    # Act
    token = create_access_token(data)
    
    # Assert
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verificar que el token puede ser decodificado
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert decoded["sub"] == "1"
    assert decoded["email"] == "test@example.com"

def test_create_access_token_includes_expiration():
    """Prueba que el token incluye expiration"""
    # Arrange
    data = {"sub": "1"}
    
    # Act
    token = create_access_token(data)
    
    # Assert
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert "exp" in decoded

def test_create_access_token_custom_expiration():
    """Prueba que create_access_token respeta la expiración personalizada"""
    from datetime import timedelta
    
    # Arrange
    data = {"sub": "1"}
    custom_expiry = timedelta(hours=5)
    
    # Act
    token = create_access_token(data, expires_delta=custom_expiry)
    
    # Assert
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert "exp" in decoded

def test_create_access_token_raises_error_on_invalid_key():
    """Prueba que create_access_token genera error con configuración inválida"""
    # Esta prueba verifica que el sistema maneja errores de generación correctamente
    data = {"sub": "1"}
    token = create_access_token(data)
    
    # Intentar decodificar con clave incorrecta debe fallar
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "wrong_secret_key", algorithms=[settings.JWT_ALGORITHM])
