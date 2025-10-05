from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UUID, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.config.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization_models import Sucursal, Rol

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

    __table_args__ = (
        CheckConstraint("id_usuario != id_supervisor", name="chk_usuario_no_supervisor"),
    )

    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    sucursal = relationship("Sucursal", back_populates="usuarios")
    sesiones = relationship("SesionUsuario", back_populates="usuario")
    kardex_registrados = relationship("Kardex", back_populates="usuario")
    movimientos_registrados = relationship("Movimiento", back_populates="usuario")

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

