from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Numeric, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.auth_models import Usuario
    from app.models.organization_models import Sucursal

# Tabla intermedia para la relación many-to-many entre Producto y Proveedor
producto_proveedor = Table(
    "producto_proveedor",
    Base.metadata,
    Column("id_producto", Integer, ForeignKey("producto.id_producto"), primary_key=True),
    Column("id_proveedor", Integer, ForeignKey("proveedor.id_proveedor"), primary_key=True)
)

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    productos = relationship("Producto", back_populates="categoria")

class Marca(Base):
    __tablename__ = "marca"

    id_marca = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    productos = relationship("Producto", back_populates="marca")

class Producto(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_producto = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))
    id_marca = Column(Integer, ForeignKey("marca.id_marca"))
    unidad_medida = Column(String(10), default="UNIDAD")
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Check constraint para unidad_medida
    __table_args__ = (
        CheckConstraint(
            unidad_medida.in_(['UNIDAD', 'KG', 'GRAMO', 'LITRO', 'ML', 'METRO', 'CM']),
            name='producto_unidad_medida_check'
        ),
    )

    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    marca = relationship("Marca", back_populates="productos")
    precios = relationship("PrecioProducto", back_populates="producto")
    proveedores = relationship("Proveedor", secondary=producto_proveedor, back_populates="productos")
    inventarios = relationship("Inventario", back_populates="producto")

class PrecioProducto(Base):
    __tablename__ = "precio_producto"

    id_precio = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), default=datetime.utcnow)
    fecha_fin = Column(DateTime(timezone=True))

    # Relaciones
    producto = relationship("Producto", back_populates="precios")

class Proveedor(Base):
    __tablename__ = "proveedor"

    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    contacto = Column(String(100))
    email = Column(String(100))
    telefono = Column(String(20))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relaciones
    productos = relationship("Producto", secondary=producto_proveedor, back_populates="proveedores")

class Almacen(Base):
    __tablename__ = "almacen"

    id_almacen = Column(Integer, primary_key=True, index=True)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=False)
    nombre = Column(String(100), nullable=False)
    codigo_almacen = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Relaciones
    sucursal = relationship("Sucursal", back_populates="almacenes")
    ubicaciones = relationship("Ubicacion", back_populates="almacen")

class Ubicacion(Base):
    __tablename__ = "ubicacion"

    id_ubicacion = Column(Integer, primary_key=True, index=True)
    id_almacen = Column(Integer, ForeignKey("almacen.id_almacen"), nullable=False)
    nombre = Column(String(100), nullable=False)
    codigo_ubicacion = Column(String(20), nullable=False)
    tipo_ubicacion = Column(String(20), default="ESTANTERIA")
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Check constraint para tipo_ubicacion
    __table_args__ = (
        CheckConstraint(
            tipo_ubicacion.in_(['ESTANTERIA', 'REFRIGERADO', 'SECO', 'LIQUIDOS', 'OTROS']),
            name='ubicacion_tipo_ubicacion_check'
        ),
    )

    # Relaciones
    almacen = relationship("Almacen", back_populates="ubicaciones")
    inventarios = relationship("Inventario", back_populates="ubicacion")

class Inventario(Base):
    __tablename__ = "inventario"

    id_inventario = Column(Integer, primary_key=True, index=True)
    id_ubicacion = Column(Integer, ForeignKey("ubicacion.id_ubicacion"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad_actual = Column(Numeric(10, 2), default=0, nullable=False)
    stock_minimo = Column(Numeric(10, 2), default=0)
    fecha_ultima_actualizacion = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="inventarios")
    producto = relationship("Producto", back_populates="inventarios")
    kardex = relationship("Kardex", back_populates="inventario")
    alertas = relationship("AlertaStock", back_populates="inventario")

class MotivoMovimiento(Base):
    __tablename__ = "motivo_movimiento"

    id_motivo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    tipo_movimiento = Column(String(10), nullable=False)
    tipo_incidencia = Column(String(50))
    activo = Column(Boolean, default=True)

    # Check constraint para tipo_movimiento
    __table_args__ = (
        CheckConstraint(
            tipo_movimiento.in_(['INGRESO', 'EGRESO']),
            name='motivo_movimiento_tipo_movimiento_check'
        ),
    )

    # Relaciones
    kardex = relationship("Kardex", back_populates="motivo")
    movimientos = relationship("Movimiento", back_populates="motivo")

class Kardex(Base):
    __tablename__ = "kardex"

    id_kardex = Column(Integer, primary_key=True, index=True)
    id_inventario = Column(Integer, ForeignKey("inventario.id_inventario"), nullable=False)
    tipo_movimiento = Column(String(10), nullable=False)
    id_motivo = Column(Integer, ForeignKey("motivo_movimiento.id_motivo"), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    cantidad_anterior = Column(Numeric(10, 2), nullable=False)
    cantidad_nueva = Column(Numeric(10, 2), nullable=False)
    observacion = Column(String(500))
    numero_documento = Column(String(50))
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_movimiento = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Check constraint para tipo_movimiento
    __table_args__ = (
        CheckConstraint(
            tipo_movimiento.in_(['INGRESO', 'EGRESO']),
            name='kardex_tipo_movimiento_check'
        ),
    )

    # Relaciones
    inventario = relationship("Inventario", back_populates="kardex")
    motivo = relationship("MotivoMovimiento", back_populates="kardex")
    usuario = relationship("Usuario", backref="kardex_registrados")

class Movimiento(Base):
    __tablename__ = "movimiento"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    tipo_movimiento = Column(String(10), nullable=False)
    id_motivo = Column(Integer, ForeignKey("motivo_movimiento.id_motivo"), nullable=False)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"))
    numero_documento = Column(String(50))
    observacion = Column(String(500))
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_movimiento = Column(DateTime(timezone=True), default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Check constraint para tipo_movimiento
    __table_args__ = (
        CheckConstraint(
            tipo_movimiento.in_(['INGRESO', 'EGRESO']),
            name='movimiento_tipo_movimiento_check'
        ),
    )

    # Relaciones
    motivo = relationship("MotivoMovimiento", back_populates="movimientos")
    usuario = relationship("Usuario", backref="movimientos_registrados")
    detalles = relationship("MovimientoDetalle", back_populates="movimiento")

class MovimientoDetalle(Base):
    __tablename__ = "movimiento_detalle"

    id_movimiento_detalle = Column(Integer, primary_key=True, index=True)
    id_movimiento = Column(Integer, ForeignKey("movimiento.id_movimiento"), nullable=False)
    id_inventario = Column(Integer, ForeignKey("inventario.id_inventario"), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)

    # Relaciones
    movimiento = relationship("Movimiento", back_populates="detalles")
    inventario = relationship("Inventario")

class AlertaStock(Base):
    __tablename__ = "alerta_stock"

    id_alerta = Column(Integer, primary_key=True, index=True)
    id_inventario = Column(Integer, ForeignKey("inventario.id_inventario"), nullable=False)
    fecha_alerta = Column(DateTime, default=datetime.utcnow, nullable=False)
    cantidad_actual = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), nullable=False)
    observacion = Column(Text)

    # Check constraint para estado
    __table_args__ = (
        CheckConstraint(
            estado.in_(['creado', 'stock_minimo', 'stock_bajo']),
            name='chk_alerta_stock_estado'
        ),
    )

    # Relaciones
    inventario = relationship("Inventario", back_populates="alertas")