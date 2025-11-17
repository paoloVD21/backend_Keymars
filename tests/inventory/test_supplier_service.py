import pytest
from fastapi import HTTPException
from app.services.supplier_service import SupplierService
from app.schemas.supplier_schemas import SupplierCreate, SupplierUpdate
from app.models.inventory_models import Proveedor

def test_get_proveedores_activos_empty(test_db):
    """Prueba obtención de proveedores cuando no hay registros"""
    # Act
    suppliers = SupplierService.get_proveedores_activos(test_db)
    
    # Assert
    assert suppliers == []

def test_get_proveedores_activos_success(test_db, test_supplier):
    """Prueba obtención de proveedores activos"""
    # Arrange - Crear proveedor inactivo
    inactive_supplier = Proveedor(
        nombre="Inactive Supplier",
        email="inactive@test.com",
        telefono="9876543210",
        activo=False
    )
    test_db.add(inactive_supplier)
    test_db.commit()
    
    # Act
    suppliers = SupplierService.get_proveedores_activos(test_db)
    
    # Assert
    assert len(suppliers) == 1
    assert str(suppliers[0].nombre) == "Test Supplier"
    assert all(bool(sup.activo) is True for sup in suppliers)

def test_get_suppliers_empty(test_db):
    """Prueba obtención de proveedores paginado cuando no hay registros"""
    # Act
    service = SupplierService(test_db)
    result = service.get_suppliers()
    
    # Assert
    assert result["total"] == 0
    assert result["items"] == []

def test_get_suppliers_with_pagination(test_db):
    """Prueba obtención de proveedores con paginación"""
    # Arrange - Crear varios proveedores
    for i in range(5):
        supplier = Proveedor(
            nombre=f"Supplier {i}",
            email=f"supplier{i}@test.com",
            telefono=f"123456789{i}",
            activo=True
        )
        test_db.add(supplier)
    test_db.commit()
    
    # Act
    service = SupplierService(test_db)
    result = service.get_suppliers(skip=0, limit=3)
    
    # Assert
    assert result["total"] == 5
    assert len(result["items"]) == 3

def test_get_suppliers_with_search(test_db, test_supplier):
    """Prueba búsqueda de proveedores"""
    # Act
    service = SupplierService(test_db)
    result = service.get_suppliers(search="Test")
    
    # Assert
    assert result["total"] == 1
    assert result["items"][0].nombre == "Test Supplier"

def test_get_suppliers_with_active_filter(test_db):
    """Prueba filtro de proveedores activos"""
    # Arrange
    active_supplier = Proveedor(
        nombre="Active Supplier",
        email="active@test.com",
        telefono="1234567890",
        activo=True
    )
    inactive_supplier = Proveedor(
        nombre="Inactive Supplier",
        email="inactive@test.com",
        telefono="0987654321",
        activo=False
    )
    test_db.add_all([active_supplier, inactive_supplier])
    test_db.commit()
    
    # Act
    service = SupplierService(test_db)
    result = service.get_suppliers(activo=True)
    
    # Assert
    assert result["total"] == 1
    assert result["items"][0].activo is True

def test_create_supplier_success(test_db):
    """Prueba creación de proveedor exitosa"""
    # Arrange
    supplier_data = SupplierCreate(
        nombre="New Supplier",
        contacto="John Doe",
        email="newsupplier@test.com",
        telefono="1234567890"
    )
    
    # Act
    service = SupplierService(test_db)
    new_supplier = service.create_supplier(supplier_data)
    
    # Assert
    assert str(new_supplier.nombre) == "New Supplier"
    assert str(new_supplier.email) == "newsupplier@test.com"
    assert new_supplier.id_proveedor is not None

def test_get_supplier_by_id_success(test_db, test_supplier):
    """Prueba obtención de proveedor por ID"""
    # Act
    service = SupplierService(test_db)
    supplier = service.get_supplier_by_id(test_supplier.id_proveedor)
    
    # Assert
    assert supplier.id_proveedor == test_supplier.id_proveedor
    assert str(supplier.nombre) == "Test Supplier"

def test_get_supplier_by_id_not_found(test_db):
    """Prueba obtención de proveedor con ID inexistente"""
    # Act & Assert
    service = SupplierService(test_db)
    with pytest.raises(HTTPException) as exc_info:
        service.get_supplier_by_id(9999)
    assert exc_info.value.status_code == 404
    assert "no encontrado" in exc_info.value.detail.lower()

def test_update_supplier_success(test_db, test_supplier):
    """Prueba actualización de proveedor"""
    # Arrange
    supplier_update = SupplierUpdate(
        nombre="Updated Supplier",
        contacto="Updated Contact",
        email="updated@test.com",
        telefono="9876543210"
    )
    
    # Act
    service = SupplierService(test_db)
    updated_supplier = service.update_supplier(test_supplier.id_proveedor, supplier_update)
    
    # Assert
    assert str(updated_supplier.nombre) == "Updated Supplier"
    assert str(updated_supplier.email) == "updated@test.com"

def test_toggle_supplier_status(test_db, test_supplier):
    """Prueba cambio de estado del proveedor"""
    # Arrange
    original_status = test_supplier.activo
    
    # Act
    service = SupplierService(test_db)
    updated_supplier = service.toggle_supplier_status(test_supplier.id_proveedor)
    
    # Assert
    assert updated_supplier.activo != original_status
    assert bool(updated_supplier.activo) is False

def test_toggle_supplier_status_twice(test_db, test_supplier):
    """Prueba cambio de estado del proveedor dos veces"""
    # Arrange
    original_status = test_supplier.activo
    
    # Act
    service = SupplierService(test_db)
    service.toggle_supplier_status(test_supplier.id_proveedor)
    toggled_again = service.toggle_supplier_status(test_supplier.id_proveedor)
    
    # Assert
    assert toggled_again.activo == original_status
