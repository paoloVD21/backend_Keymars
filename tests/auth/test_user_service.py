import pytest
from fastapi import HTTPException
from app.services.user_service import UserService
from app.schemas import user_schemas
from app.utils.auth import get_password_hash
from app.models.auth_models import Usuario

def test_get_users_empty(test_db):
    """Prueba obtención de usuarios cuando no hay registros"""
    # Act
    service = UserService(test_db)
    usuarios, total = service.get_users()
    
    # Assert
    assert usuarios == []
    assert total == 0

def test_get_users_with_pagination(test_db, test_sucursal, test_rol):
    """Prueba obtención de usuarios con paginación"""
    # Arrange - Crear varios usuarios
    for i in range(5):
        user = Usuario(
            email=f"user{i}@test.com",
            password_hash=get_password_hash("password123"),
            nombre=f"User{i}",
            apellido="Test",
            id_sucursal=test_sucursal.id_sucursal,
            id_rol=test_rol.id_rol,
            activo=True
        )
        test_db.add(user)
    test_db.commit()
    
    # Act
    service = UserService(test_db)
    usuarios, total = service.get_users(skip=0, limit=3)
    
    # Assert
    assert len(usuarios) == 3
    assert total == 5

def test_get_users_with_search(test_db, test_sucursal, test_rol):
    """Prueba búsqueda de usuarios por nombre"""
    # Arrange
    user = Usuario(
        email="john@test.com",
        password_hash=get_password_hash("password123"),
        nombre="John",
        apellido="Doe",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        activo=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Act
    service = UserService(test_db)
    usuarios, total = service.get_users(search="John")
    
    # Assert
    assert len(usuarios) == 1
    assert str(usuarios[0].nombre) == "John"

def test_get_users_with_active_filter(test_db, test_sucursal, test_rol):
    """Prueba filtro de usuarios activos"""
    # Arrange
    active_user = Usuario(
        email="active@test.com",
        password_hash=get_password_hash("password123"),
        nombre="Active",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        activo=True
    )
    inactive_user = Usuario(
        email="inactive@test.com",
        password_hash=get_password_hash("password123"),
        nombre="Inactive",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        activo=False
    )
    test_db.add(active_user)
    test_db.add(inactive_user)
    test_db.commit()
    
    # Act
    service = UserService(test_db)
    usuarios, total = service.get_users(activo=True)
    
    # Assert
    assert len(usuarios) == 1
    assert bool(usuarios[0].activo) is True

def test_create_user_success(test_db, test_sucursal, test_rol):
    """Prueba creación de usuario exitosa"""
    # Arrange
    user_data = user_schemas.UserCreate(
        email="newuser@test.com",
        password="password123",
        nombre="New",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol
    )
    
    # Act
    service = UserService(test_db)
    new_user = service.create_user(user_data)
    
    # Assert
    assert str(new_user.email) == "newuser@test.com"
    assert str(new_user.nombre) == "New"
    assert bool(new_user.activo) is True
    assert new_user.id_usuario is not None

def test_create_user_duplicate_email(test_db, test_sucursal, test_rol, test_user):
    """Prueba creación de usuario con email duplicado"""
    # Arrange
    user_data = user_schemas.UserCreate(
        email=test_user.email,  # Email que ya existe
        password="password123",
        nombre="Another",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol
    )
    
    # Act & Assert
    service = UserService(test_db)
    with pytest.raises(HTTPException) as exc_info:
        service.create_user(user_data)
    assert exc_info.value.status_code == 400
    assert "email ya está registrado" in exc_info.value.detail

def test_create_user_invalid_supervisor(test_db, test_sucursal, test_rol):
    """Prueba creación de usuario con supervisor inválido"""
    # Arrange
    user_data = user_schemas.UserCreate(
        email="newuser@test.com",
        password="password123",
        nombre="New",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        id_supervisor=9999  # ID de supervisor que no existe
    )
    
    # Act & Assert
    service = UserService(test_db)
    with pytest.raises(HTTPException) as exc_info:
        service.create_user(user_data)
    assert exc_info.value.status_code == 400
    assert "supervisor" in exc_info.value.detail.lower()

def test_create_user_with_supervisor(test_db, test_sucursal, test_rol, test_user):
    """Prueba creación de usuario con supervisor válido"""
    # Arrange
    user_data = user_schemas.UserCreate(
        email="subordinate@test.com",
        password="password123",
        nombre="Subordinate",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        id_supervisor=test_user.id_usuario
    )
    
    # Act
    service = UserService(test_db)
    new_user = service.create_user(user_data)
    
    # Assert
    assert new_user.id_supervisor == test_user.id_usuario

def test_get_user_by_id_success(test_db, test_user):
    """Prueba obtención de usuario por email usando get_users con búsqueda"""
    # Act
    service = UserService(test_db)
    usuarios, total = service.get_users(search=test_user.email)
    
    # Assert
    assert total >= 1
    found_user = next((u for u in usuarios if u.email == test_user.email), None)
    assert found_user is not None
    assert found_user.id_usuario == test_user.id_usuario

def test_get_user_not_found(test_db):
    """Prueba obtención de usuario inexistente usando búsqueda"""
    # Act
    service = UserService(test_db)
    usuarios, total = service.get_users(search="nonexistent@test.com")
    
    # Assert
    assert total == 0
    assert usuarios == []

def test_update_user_success(test_db, test_user):
    """Prueba actualización de usuario"""
    # Arrange
    user_update = user_schemas.UserUpdate(
        nombre="Updated",
        apellido="Name"
    )
    
    # Act
    service = UserService(test_db)
    updated_user = service.update_user(test_user.id_usuario, user_update)
    
    # Assert
    # Refrescar el usuario para obtener los cambios
    test_db.refresh(updated_user)
    assert str(updated_user.nombre) == "Updated"
    assert str(updated_user.apellido) == "Name"

def test_toggle_user_status(test_db, test_user):
    """Prueba cambio de estado del usuario"""
    # Arrange
    original_status = bool(test_user.activo)
    
    # Act
    service = UserService(test_db)
    updated_user = service.toggle_user_status(test_user.id_usuario, not original_status)
    
    # Assert
    test_db.refresh(updated_user)
    assert bool(updated_user.activo) != original_status
