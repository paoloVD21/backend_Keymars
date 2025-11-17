import pytest
from fastapi import HTTPException
from app.services.product_service import ProductService
from app.schemas import product_schemas
from app.models.inventory_models import Producto, Inventario
from decimal import Decimal

def test_get_products_empty(test_db):
    """Prueba obtención de productos cuando no hay registros"""
    # Act
    service = ProductService(test_db)
    result = service.get_products()
    
    # Assert
    assert result["total"] == 0
    assert result["items"] == []

def test_get_products_with_pagination(test_db, test_category, test_brand, test_supplier):
    """Prueba obtención de productos con paginación"""
    # Arrange - Crear varios productos
    for i in range(5):
        product = Producto(
            codigo_producto=f"PROD-{i:03d}",
            nombre=f"Product {i}",
            unidad_medida="UNIDAD",
            id_categoria=test_category.id_categoria,
            id_marca=test_brand.id_marca,
            id_proveedor=test_supplier.id_proveedor,
            precio=Decimal(f"{10 + i}.99"),
            activo=True
        )
        test_db.add(product)
    test_db.commit()
    
    # Act
    service = ProductService(test_db)
    result = service.get_products(skip=0, limit=3)
    
    # Assert
    assert result["total"] == 5
    assert len(result["items"]) <= 3

def test_get_products_with_search(test_db, test_category, test_brand, test_supplier):
    """Prueba búsqueda de productos"""
    # Arrange
    product = Producto(
        codigo_producto="LAPTOP-001",
        nombre="Laptop Dell",
        unidad_medida="UNIDAD",
        id_categoria=test_category.id_categoria,
        id_marca=test_brand.id_marca,
        id_proveedor=test_supplier.id_proveedor,
        precio=Decimal("999.99"),
        activo=True
    )
    test_db.add(product)
    test_db.commit()
    
    # Act
    service = ProductService(test_db)
    result = service.get_products(search="Laptop")
    
    # Assert
    assert result["total"] == 1
    assert len(result["items"]) > 0

def test_get_products_with_active_filter(test_db, test_category, test_brand, test_supplier):
    """Prueba filtro de productos activos"""
    # Arrange
    active_product = Producto(
        codigo_producto="ACTIVE-001",
        nombre="Active Product",
        unidad_medida="UNIDAD",
        id_categoria=test_category.id_categoria,
        id_marca=test_brand.id_marca,
        id_proveedor=test_supplier.id_proveedor,
        precio=Decimal("50.00"),
        activo=True
    )
    inactive_product = Producto(
        codigo_producto="INACTIVE-001",
        nombre="Inactive Product",
        unidad_medida="UNIDAD",
        id_categoria=test_category.id_categoria,
        id_marca=test_brand.id_marca,
        id_proveedor=test_supplier.id_proveedor,
        precio=Decimal("50.00"),
        activo=False
    )
    test_db.add_all([active_product, inactive_product])
    test_db.commit()
    
    # Act
    service = ProductService(test_db)
    result = service.get_products(activo=True)
    
    # Assert
    assert result["total"] == 1

def test_create_product_success(test_db, test_category, test_brand, test_supplier, test_location):
    """Prueba creación de producto exitosa"""
    # Arrange
    product_data = product_schemas.ProductCreate(
        codigo_producto="NEW-PROD-001",
        nombre="New Product",
        descripcion="Descripción del nuevo producto",
        id_categoria=test_category.id_categoria,
        id_marca=test_brand.id_marca,
        id_proveedor=test_supplier.id_proveedor,
        unidad_medida="UNIDAD",
        precio=Decimal("75.50"),
        stock_minimo=Decimal("5")
    )
    
    # Act
    service = ProductService(test_db)
    new_product = service.create_product(product_data)
    
    # Assert
    # create_product retorna un dict
    assert new_product["nombre"] == "New Product"
    assert new_product["codigo_producto"] == "NEW-PROD-001"
    assert new_product["id_producto"] is not None

def test_get_product_by_id_success(test_db, test_product):
    """Prueba obtención de producto por ID"""
    # Act
    service = ProductService(test_db)
    product = service.get_product_by_id(test_product.id_producto)
    
    # Assert
    assert product["id_producto"] == test_product.id_producto
    assert product["nombre"] == "Test Product"

def test_get_product_by_id_not_found(test_db):
    """Prueba obtención de producto con ID inexistente"""
    # Act & Assert
    service = ProductService(test_db)
    with pytest.raises(HTTPException) as exc_info:
        service.get_product_by_id(9999)
    assert exc_info.value.status_code == 404

def test_update_product_success(test_db, test_product):
    """Prueba actualización de producto"""
    # Arrange
    product_update = product_schemas.ProductUpdate(
        codigo_producto="UPDATED-001",
        nombre="Updated Product",
        descripcion="Updated Description",
        id_categoria=test_product.id_categoria,
        unidad_medida="UNIDAD",
        precio=Decimal("150.00")
    )
    
    # Act
    service = ProductService(test_db)
    updated_product = service.update_product(test_product.id_producto, product_update)
    
    # Assert
    assert updated_product["nombre"] == "Updated Product"
    assert updated_product["precio"] == Decimal("150.00")

def test_toggle_product_status(test_db, test_product):
    """Prueba cambio de estado del producto"""
    # Arrange
    original_status = test_product.activo
    
    # Act
    service = ProductService(test_db)
    result = service.toggle_product_status(test_product.id_producto)
    
    # Assert
    # El resultado es un dict con la información del producto
    assert result["activo"] != original_status
    assert result["activo"] is False

def test_get_product_inventory_info(test_db, test_product, test_location):
    """Prueba obtención de información de inventario del producto"""
    # Arrange
    inventory = Inventario(
        id_producto=test_product.id_producto,
        id_ubicacion=test_location.id_ubicacion,
        cantidad_actual=100,
        stock_minimo=10
    )
    test_db.add(inventory)
    test_db.commit()
    
    # Act
    service = ProductService(test_db)
    result = service.get_product_by_id(test_product.id_producto)
    
    # Assert
    assert result["id_producto"] == test_product.id_producto
