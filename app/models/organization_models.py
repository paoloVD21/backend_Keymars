from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base
# Importamos solo el tipo para evitar importación circular
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.auth_models import Usuario
    from app.models.inventory_models import Ubicacion, Movimiento

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
    modulo = Column(String(50))
    activo = Column(Boolean, default=True)

    # Relaciones
    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")

class Sucursal(Base):
    __tablename__ = "sucursal"

    id_sucursal = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(Text)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="sucursal")
    ubicaciones = relationship("Ubicacion", back_populates="sucursal")
    movimientos = relationship("Movimiento", back_populates="sucursal")

class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    es_supervisor = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("Permiso", secondary=rol_permiso, back_populates="roles")