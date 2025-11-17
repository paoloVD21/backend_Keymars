import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base, get_db
# Importar todos los modelos para que se registren en Base.metadata
from app.models import (
    Usuario, SesionUsuario,
    Sucursal, Rol, Permiso,
    Categoria, Marca, Producto, Proveedor,
    Ubicacion, Inventario, MotivoMovimiento,
    Kardex, Movimiento, Alert
)
from app.utils.auth import get_password_hash
from main import app
import os

# Usar una base de datos SQLite en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Fixture que crea una base de datos limpia para cada test"""
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_sucursal(test_db):
    """Fixture que crea una sucursal de prueba"""
    sucursal = Sucursal(
        nombre="Sucursal Test",
        direccion="Dirección Test",
        activo=True
    )
    test_db.add(sucursal)
    test_db.commit()
    test_db.refresh(sucursal)
    return sucursal

@pytest.fixture
def test_rol(test_db):
    """Fixture que crea un rol de prueba"""
    rol = Rol(
        nombre="Administrador",
        es_supervisor=False,
        activo=True
    )
    test_db.add(rol)
    test_db.commit()
    test_db.refresh(rol)
    return rol

@pytest.fixture
def test_user(test_db, test_sucursal, test_rol):
    """Fixture que crea un usuario de prueba con contraseña correcta"""
    password = "password123"
    user = Usuario(
        email="test@example.com",
        password_hash=get_password_hash(password),
        nombre="Test",
        apellido="User",
        id_sucursal=test_sucursal.id_sucursal,
        id_rol=test_rol.id_rol,
        activo=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def client(test_db):
    """Fixture que crea un cliente de prueba con la DB inyectada"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_category(test_db):
    """Fixture que crea una categoría de prueba"""
    categoria = Categoria(
        nombre="Test Category",
        activo=True
    )
    test_db.add(categoria)
    test_db.commit()
    test_db.refresh(categoria)
    return categoria

@pytest.fixture
def test_brand(test_db):
    """Fixture que crea una marca de prueba"""
    marca = Marca(
        nombre="Test Brand",
        activo=True
    )
    test_db.add(marca)
    test_db.commit()
    test_db.refresh(marca)
    return marca

@pytest.fixture
def test_supplier(test_db):
    """Fixture que crea un proveedor de prueba"""
    proveedor = Proveedor(
        nombre="Test Supplier",
        email="supplier@test.com",
        telefono="1234567890",
        activo=True
    )
    test_db.add(proveedor)
    test_db.commit()
    test_db.refresh(proveedor)
    return proveedor

@pytest.fixture
def test_product(test_db, test_category, test_brand, test_supplier, test_location):
    """Fixture que crea un producto de prueba"""
    from decimal import Decimal
    producto = Producto(
        codigo_producto="TEST-001",
        nombre="Test Product",
        descripcion="Descripción de producto de prueba",
        id_categoria=test_category.id_categoria,
        id_marca=test_brand.id_marca,
        id_proveedor=test_supplier.id_proveedor,
        precio=Decimal("99.99"),
        activo=True
    )
    test_db.add(producto)
    test_db.commit()
    test_db.refresh(producto)
    
    # Crear entrada de inventario para el producto
    from app.models.inventory_models import Inventario
    inventario = Inventario(
        id_producto=producto.id_producto,
        id_ubicacion=test_location.id_ubicacion,
        cantidad_actual=100,
        stock_minimo=5
    )
    test_db.add(inventario)
    test_db.commit()
    
    return producto

@pytest.fixture
def test_location(test_db, test_sucursal):
    """Fixture que crea una ubicación de prueba"""
    ubicacion = Ubicacion(
        nombre="Test Location",
        codigo_ubicacion="TL-001",
        tipo_ubicacion="ESTANTERIA",
        id_sucursal=test_sucursal.id_sucursal,
        activo=True
    )
    test_db.add(ubicacion)
    test_db.commit()
    test_db.refresh(ubicacion)
    return ubicacion
