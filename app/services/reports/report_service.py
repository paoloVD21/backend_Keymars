from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models import (
    Inventario, Producto, Ubicacion, Kardex, Movimiento,
    MovimientoDetalle
)

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def _get_date_range(self, periodo: str) -> tuple[datetime, datetime]:
        """
        Calcula el rango de fechas basado en el periodo
        """
        end_date = datetime.now()
        if periodo == "ultimo_mes":
            start_date = end_date - timedelta(days=30)
        elif periodo == "ultimo_trimestre":
            start_date = end_date - timedelta(days=90)
        elif periodo == "ultimo_anio":
            start_date = end_date - timedelta(days=365)
        else:
            raise ValueError("Período no válido")
        
        return start_date, end_date

    def get_inventory_summary(self, periodo: str, sucursal_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el resumen de inventario para una sucursal específica
        """
        inventory_data = (
            self.db.query(
                Producto.codigo_producto,
                Producto.nombre,
                Ubicacion.nombre.label('ubicacion'),
                Inventario.cantidad_actual,
                Inventario.stock_minimo,
                (Inventario.cantidad_actual * Producto.precio).label('valor_total')
            )
            .join(Producto, Inventario.id_producto == Producto.id_producto)
            .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
            .filter(
                Ubicacion.id_sucursal == sucursal_id,
                Producto.activo == True,
                Ubicacion.activo == True
            )
            .all()
        )

        return [
            {
                'codigo_producto': item.codigo_producto,
                'nombre_producto': item.nombre,
                'ubicacion': item.ubicacion,
                'stock_actual': float(item.cantidad_actual),
                'stock_minimo': float(item.stock_minimo),
                'valor_total': float(item.valor_total)
            }
            for item in inventory_data
        ]

    def get_low_stock_report(self, periodo: str, sucursal_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el reporte de productos con stock bajo
        """
        low_stock_data = (
            self.db.query(
                Producto.codigo_producto,
                Producto.nombre,
                Ubicacion.nombre.label('ubicacion'),
                Inventario.cantidad_actual,
                Inventario.stock_minimo,
                (Inventario.cantidad_actual - Inventario.stock_minimo).label('diferencia')
            )
            .join(Producto, Inventario.id_producto == Producto.id_producto)
            .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
            .filter(
                Ubicacion.id_sucursal == sucursal_id,
                Producto.activo == True,
                Ubicacion.activo == True,
                Inventario.cantidad_actual <= Inventario.stock_minimo
            )
            .order_by(func.abs(Inventario.cantidad_actual - Inventario.stock_minimo).desc())
            .all()
        )

        return [
            {
                'codigo_producto': item.codigo_producto,
                'nombre_producto': item.nombre,
                'ubicacion': item.ubicacion,
                'stock_actual': float(item.cantidad_actual),
                'stock_minimo': float(item.stock_minimo),
                'diferencia': float(item.diferencia)
            }
            for item in low_stock_data
        ]

    def get_movement_summary(self, periodo: str, sucursal_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el resumen de movimientos para el período especificado
        """
        start_date, end_date = self._get_date_range(periodo)
        
        # Consulta principal para los movimientos con filtro de sucursal
        movement_data = (
            self.db.query(
                Producto.codigo_producto,
                Producto.nombre,
                func.sum(case(
                    {Kardex.tipo_movimiento == 'INGRESO': Kardex.cantidad},
                    else_=0
                )).label('total_entradas'),
                func.sum(case(
                    {Kardex.tipo_movimiento == 'EGRESO': Kardex.cantidad},
                    else_=0
                )).label('total_salidas'),
                func.count(Kardex.id_kardex).label('movimientos_totales')
            )
            .join(Inventario, Kardex.id_inventario == Inventario.id_inventario)
            .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
            .join(Producto, Inventario.id_producto == Producto.id_producto)
            .filter(
                Kardex.fecha_movimiento.between(start_date, end_date),
                Ubicacion.id_sucursal == sucursal_id
            )
            .group_by(Producto.codigo_producto, Producto.nombre)
            .order_by(func.count(Kardex.id_kardex).desc())
            .all()
        )

        return [
            {
                'codigo_producto': item.codigo_producto,
                'nombre_producto': item.nombre,
                'total_entradas': float(item.total_entradas),
                'total_salidas': float(item.total_salidas),
                'movimientos_totales': item.movimientos_totales
            }
            for item in movement_data
        ]