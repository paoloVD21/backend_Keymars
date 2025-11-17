import pytest
from app.services.organization_service import OrganizationService
from app.models.organization_models import Rol, Sucursal

def test_get_roles_empty(test_db):
    """Prueba obtención de roles cuando no hay registros"""
    # Act
    roles = OrganizationService.get_roles(test_db)
    
    # Assert
    assert roles == []

def test_get_roles_success(test_db, test_rol):
    """Prueba obtención de roles activos"""
    # Arrange - Crear rol inactivo
    inactive_rol = Rol(
        nombre="Inactive Role",
        es_supervisor=False,
        activo=False
    )
    test_db.add(inactive_rol)
    test_db.commit()
    
    # Act
    roles = OrganizationService.get_roles(test_db)
    
    # Assert
    assert len(roles) == 1
    assert str(roles[0].nombre) == "Administrador"
    assert all(bool(rol.activo) is True for rol in roles)

def test_get_roles_multiple(test_db):
    """Prueba obtención de múltiples roles activos"""
    # Arrange
    rol1 = Rol(nombre="Admin", activo=True)
    rol2 = Rol(nombre="User", activo=True)
    rol3 = Rol(nombre="Guest", activo=True)
    test_db.add_all([rol1, rol2, rol3])
    test_db.commit()
    
    # Act
    roles = OrganizationService.get_roles(test_db)
    
    # Assert
    assert len(roles) == 3
    nombres = [rol.nombre for rol in roles]
    assert "Admin" in nombres
    assert "User" in nombres
    assert "Guest" in nombres

def test_get_sucursales_empty(test_db):
    """Prueba obtención de sucursales cuando no hay registros"""
    # Act
    sucursales = OrganizationService.get_sucursales(test_db)
    
    # Assert
    assert sucursales == []

def test_get_sucursales_success(test_db, test_sucursal):
    """Prueba obtención de sucursales activas"""
    # Arrange - Crear sucursal inactiva
    inactive_sucursal = Sucursal(
        nombre="Sucursal Inactiva",
        direccion="Dirección Inactiva",
        activo=False
    )
    test_db.add(inactive_sucursal)
    test_db.commit()
    
    # Act
    sucursales = OrganizationService.get_sucursales(test_db)
    
    # Assert
    assert len(sucursales) == 1
    assert str(sucursales[0].nombre) == "Sucursal Test"
    assert all(bool(suc.activo) is True for suc in sucursales)

def test_get_sucursales_multiple(test_db):
    """Prueba obtención de múltiples sucursales activas"""
    # Arrange
    suc1 = Sucursal(nombre="Sucursal 1", direccion="Dir 1", activo=True)
    suc2 = Sucursal(nombre="Sucursal 2", direccion="Dir 2", activo=True)
    suc3 = Sucursal(nombre="Sucursal 3", direccion="Dir 3", activo=True)
    test_db.add_all([suc1, suc2, suc3])
    test_db.commit()
    
    # Act
    sucursales = OrganizationService.get_sucursales(test_db)
    
    # Assert
    assert len(sucursales) == 3
    nombres = [suc.nombre for suc in sucursales]
    assert "Sucursal 1" in nombres
    assert "Sucursal 2" in nombres
    assert "Sucursal 3" in nombres
