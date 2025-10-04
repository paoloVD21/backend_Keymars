from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.config.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), nullable=False)
    id_supervisor = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    sucursal = relationship("Sucursal", back_populates="usuarios")
    sesiones = relationship("SesionUsuario", back_populates="usuario")

class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    es_supervisor = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("Permiso", secondary="rol_permiso", back_populates="roles")

class SesionUsuario(Base):
    __tablename__ = "sesion_usuario"

    id_sesion = Column(UUID, primary_key=True, default=uuid.uuid4)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    token_sesion = Column(String(255), unique=True, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), default=datetime.utcnow)
    fecha_expiracion = Column(DateTime(timezone=True))
    activa = Column(Boolean, default=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")

class Permiso(Base):
    __tablename__ = "permiso"

    id_permiso = Column(Integer, primary_key=True, index=True)
    modulo = Column(String(50))
    activo = Column(Boolean, default=True)

    # Relaciones
    roles = relationship("Rol", secondary="rol_permiso", back_populates="permisos")