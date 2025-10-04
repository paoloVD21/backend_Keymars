import pytest
from app.utils.auth import get_password_hash, verify_password

def test_password_hash_generation():
    """Prueba la generación y verificación del hash de contraseña"""
    # Arrange
    test_password = "contraseña_prueba"
    
    # Act
    hashed = get_password_hash(test_password)
    hash_parts = hashed.split("$")
    is_valid = verify_password(test_password, hashed)
    
    # Assert
    assert hash_parts[0] == "scrypt", "El algoritmo debe ser scrypt"
    assert len(hash_parts) == 3, "El formato debe ser scrypt$salt$hash"
    assert is_valid, "La verificación de la contraseña debe ser exitosa"

def test_password_hash_invalid_verification():
    """Prueba que la verificación falle con contraseña incorrecta"""
    # Arrange
    correct_password = "contraseña_correcta"
    wrong_password = "contraseña_incorrecta"
    
    # Act
    hashed = get_password_hash(correct_password)
    is_valid = verify_password(wrong_password, hashed)
    
    # Assert
    assert not is_valid, "La verificación debe fallar con contraseña incorrecta"

def test_empty_password():
    """Prueba que se maneje correctamente una contraseña vacía"""
    # Arrange & Act & Assert
    with pytest.raises(Exception):
        get_password_hash("")

def test_invalid_hash_format():
    """Prueba que se maneje correctamente un hash con formato inválido"""
    # Arrange
    test_password = "contraseña_prueba"
    invalid_hash = "formato_invalido"
    
    # Act
    is_valid = verify_password(test_password, invalid_hash)
    
    # Assert
    assert not is_valid, "La verificación debe fallar con formato de hash inválido"