import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base, get_db
from app.models.auth_models import Usuario
from main import app
import os

# Usar una base de datos SQLite en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    # Crear las tablas en la base de datos de prueba
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión de prueba
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpiar la base de datos después de las pruebas
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    # Sobreescribir la dependencia de base de datos
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    # Crear un usuario de prueba
    user = Usuario(
        email="test@example.com",
        password_hash="scrypt$salt$hash",  # Hash de prueba
        nombre="Test",
        apellido="User",
        id_sucursal=1,
        id_rol=1,
        activo=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user