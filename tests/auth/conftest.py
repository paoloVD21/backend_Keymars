import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base, get_db
from app.models.auth_models import Usuario, SesionUsuario
from app.models.organization_models import Sucursal, Rol
from app.utils.auth import get_password_hash
from main import app

# Este conftest.py es específico de tests de autenticación
# Las fixtures compartidas están en tests/conftest.py
