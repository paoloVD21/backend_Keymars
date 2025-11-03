from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_
from datetime import datetime, timedelta
from typing import Dict, List
from app.models.inventory_models import (
    Producto, Proveedor, Inventario, Movimiento,
    Categoria, MovimientoDetalle
)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_general_stats(self) -> Dict:
        """
        Obtiene estadísticas generales y tendencias
        """
        # Estadísticas actuales
        total_productos = self.db.query(Producto).filter(Producto.activo == True).count()
        stock_disponible = float(self.db.query(func.sum(Inventario.cantidad_actual)).scalar() or 0)
        proveedores_activos = self.db.query(Proveedor).filter(Proveedor.activo == True).count()

        # Calcular tendencias (comparando con el mes anterior)
        hoy = datetime.now()
        mes_actual = datetime(hoy.year, hoy.month, 1)
        mes_anterior = mes_actual - timedelta(days=1)
        mes_anterior = datetime(mes_anterior.year, mes_anterior.month, 1)

        # Tendencias de productos
        productos_mes_anterior = self.db.query(Producto).filter(
            and_(
                Producto.activo == True,
                Producto.fecha_creacion < mes_actual
            )
        ).count()

        tendencia_productos = self._calcular_tendencia(total_productos, productos_mes_anterior)

        # Tendencias de stock
        stock_mes_anterior = float(self.db.query(func.sum(Inventario.cantidad_actual))
            .filter(Inventario.fecha_ultima_actualizacion < mes_actual)
            .scalar() or 0)

        tendencia_stock = self._calcular_tendencia(stock_disponible, stock_mes_anterior)

        # Tendencias de proveedores
        proveedores_mes_anterior = self.db.query(Proveedor).filter(
            and_(
                Proveedor.activo == True,
                Proveedor.fecha_creacion < mes_actual
            )
        ).count()

        tendencia_proveedores = self._calcular_tendencia(proveedores_activos, proveedores_mes_anterior)

        return {
            "totalProductos": total_productos,
            "stockDisponible": stock_disponible,
            "proveedoresActivos": proveedores_activos,
            "tendencias": {
                "productos": tendencia_productos,
                "stock": tendencia_stock,
                "proveedores": tendencia_proveedores
            }
        }

    def get_movimientos_mensuales(self) -> Dict:
        """
        Obtiene estadísticas de movimientos mensuales por tipo (INGRESO/EGRESO)
        """
        # Obtener los últimos 12 meses
        hoy = datetime.now()
        meses = []
        entradas = []
        salidas = []

        for i in range(11, -1, -1):
            # Calcular el mes
            fecha = datetime(hoy.year, hoy.month, 1) - timedelta(days=i*30)
            primer_dia = datetime(fecha.year, fecha.month, 1)
            siguiente_mes = datetime(
                fecha.year + 1 if fecha.month == 12 else fecha.year,
                1 if fecha.month == 12 else fecha.month + 1,
                1
            )

            # Obtener sumas por tipo de movimiento
            resultados = (
                self.db.query(
                    Movimiento.tipo_movimiento,
                    func.coalesce(func.sum(MovimientoDetalle.cantidad), 0).label('total')
                )
                .join(MovimientoDetalle)
                .filter(
                    Movimiento.fecha_movimiento >= primer_dia,
                    Movimiento.fecha_movimiento < siguiente_mes,
                    Movimiento.activo == True
                )
                .group_by(Movimiento.tipo_movimiento)
                .all()
            )

            # Procesar resultados
            entrada_mes = 0
            salida_mes = 0
            for tipo, total in resultados:
                if tipo == 'INGRESO':
                    entrada_mes = float(total or 0)
                else:  # EGRESO
                    salida_mes = float(total or 0)

            meses.append(self._nombre_mes(fecha.month))
            entradas.append(entrada_mes)
            salidas.append(salida_mes)

        return {
            "labels": meses,
            "entradas": entradas,
            "salidas": salidas
        }

    def get_distribucion_categorias(self) -> Dict:
        """
        Obtiene la distribución de productos por categoría
        """
        resultados = (
            self.db.query(
                Categoria.nombre,
                func.count(Producto.id_producto).label('cantidad')
            )
            .join(Producto, Categoria.id_categoria == Producto.id_categoria)
            .filter(
                Producto.activo == True,
                Categoria.activo == True
            )
            .group_by(Categoria.id_categoria, Categoria.nombre)
            .order_by(func.count(Producto.id_producto).desc())
            .all()
        )

        return {
            "labels": [r.nombre for r in resultados],
            "data": [float(r.cantidad) for r in resultados]
        }

    def _calcular_tendencia(self, valor_actual: float, valor_anterior: float) -> Dict:
        """
        Calcula la tendencia entre dos valores y devuelve el porcentaje de cambio
        """
        if valor_anterior == 0:
            return {"valor": "100%" if valor_actual > 0 else "0%", "esPositivo": True}

        cambio_porcentual = ((valor_actual - valor_anterior) / valor_anterior) * 100
        return {
            "valor": f"{abs(cambio_porcentual):.1f}%",
            "esPositivo": cambio_porcentual >= 0
        }

    def _nombre_mes(self, numero_mes: int) -> str:
        """
        Convierte el número de mes a nombre en español
        """
        nombres = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return nombres[numero_mes - 1]