from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base
# Importamos solo el tipo para evitar importación circular
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.auth_models import Usuario
    from app.models.inventory_models import Almacen

class Empresa(Base):
    __tablename__ = "empresa"
    
    id_empresa = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    ruc = Column(String(20), unique=True)
    razon_social = Column(String(100))
    telefono = Column(String(20))
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Relaciones
    sucursales = relationship("Sucursal", back_populates="empresa")

# Tabla intermedia para la relación many-to-many entre Rol y Permiso
rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("id_rol", Integer, ForeignKey("rol.id_rol"), primary_key=True),
    Column("id_permiso", Integer, ForeignKey("permiso.id_permiso"), primary_key=True)
)

class Permiso(Base):
    __tablename__ = "permiso"

    id_permiso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200))
    activo = Column(Boolean, default=True)

    # Relaciones
    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")

class Sucursal(Base):
    __tablename__ = "sucursal"

    id_sucursal = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("empresa.id_empresa"), nullable=False)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(200))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relaciones
    empresa = relationship("Empresa", back_populates="sucursales")
    usuarios = relationship("Usuario", back_populates="sucursal")
    almacenes = relationship("Almacen", back_populates="sucursal")

class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    es_supervisor = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("Permiso", secondary="rol_permiso", back_populates="roles")