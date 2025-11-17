import pytest
from fastapi import HTTPException
from app.services.category_service import CategoryService
from app.services.brand_service import BrandService
from app.models.inventory_models import Categoria, Marca

def test_get_active_categories_empty(test_db):
    """Prueba obtención de categorías cuando no hay registros"""
    # Act
    categories = CategoryService.get_active_categories(test_db)
    
    # Assert
    assert categories == []

def test_get_active_categories_success(test_db, test_category):
    """Prueba obtención de categorías activas"""
    # Arrange - Crear categoría inactiva
    inactive_cat = Categoria(
        nombre="Inactive Category",
        activo=False
    )
    test_db.add(inactive_cat)
    test_db.commit()
    
    # Act
    categories = CategoryService.get_active_categories(test_db)
    
    # Assert
    assert len(categories) == 1
    assert str(categories[0].nombre) == "Test Category"
    assert all(bool(cat.activo) is True for cat in categories)

def test_get_active_categories_ordered_by_name(test_db):
    """Prueba que las categorías se devuelven ordenadas por nombre"""
    # Arrange
    cat1 = Categoria(nombre="Zebra", activo=True)
    cat2 = Categoria(nombre="Apple", activo=True)
    cat3 = Categoria(nombre="Mango", activo=True)
    test_db.add_all([cat1, cat2, cat3])
    test_db.commit()
    
    # Act
    categories = CategoryService.get_active_categories(test_db)
    
    # Assert
    names = [cat.nombre for cat in categories]
    assert names == ["Apple", "Mango", "Zebra"]

def test_get_active_brands_empty(test_db):
    """Prueba obtención de marcas cuando no hay registros"""
    # Act
    brands = BrandService.get_active_brands(test_db)
    
    # Assert
    assert brands == []

def test_get_active_brands_success(test_db, test_brand):
    """Prueba obtención de marcas activas"""
    # Arrange - Crear marca inactiva
    inactive_brand = Marca(
        nombre="Inactive Brand",
        activo=False
    )
    test_db.add(inactive_brand)
    test_db.commit()
    
    # Act
    brands = BrandService.get_active_brands(test_db)
    
    # Assert
    assert len(brands) == 1
    assert str(brands[0].nombre) == "Test Brand"
    assert all(bool(brand.activo) is True for brand in brands)

def test_get_active_brands_ordered_by_name(test_db):
    """Prueba que las marcas se devuelven ordenadas por nombre"""
    # Arrange
    brand1 = Marca(nombre="Zara", activo=True)
    brand2 = Marca(nombre="Nike", activo=True)
    brand3 = Marca(nombre="Adidas", activo=True)
    test_db.add_all([brand1, brand2, brand3])
    test_db.commit()
    
    # Act
    brands = BrandService.get_active_brands(test_db)
    
    # Assert
    names = [brand.nombre for brand in brands]
    assert names == ["Adidas", "Nike", "Zara"]
