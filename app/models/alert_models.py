from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.config.database import Base
from datetime import datetime

class Alert(Base):
    __tablename__ = "alerta_stock"

    id_alerta = Column(Integer, primary_key=True, index=True)
    id_inventario = Column(Integer, ForeignKey("inventario.id_inventario"), nullable=False)
    fecha_alerta = Column(DateTime, default=datetime.now, nullable=False)
    cantidad_actual = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), nullable=False)
    observacion = Column(Text, nullable=True)

    # Check constraint para estado
    __table_args__ = (
        CheckConstraint(
            estado.in_(['creado', 'stock_minimo', 'stock_bajo']),
            name='chk_alerta_stock_estado'
        ),
    )

    # Relaciones
    inventario = relationship("Inventario", back_populates="alertas")