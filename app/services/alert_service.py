from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from datetime import datetime
from typing import List, Optional
from app.models.alert_models import Alert
from app.schemas.alert_schemas import AlertFilter, AlertStatus
from app.models import (
    Inventario, Producto, Ubicacion, Sucursal,
    Proveedor
)

class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def get_alerts_with_filter(self, filter_params: AlertFilter) -> List[Alert]:
        """
        Obtiene las alertas aplicando los filtros especificados según los nuevos parámetros:
        - estado: Estado de la alerta (opcional)
        - id_sucursal: ID de la sucursal (opcional)
        - mes: Mes en formato "YYYY-MM" (opcional)
        """
        query = (
            self.db.query(
                Alert,
                Inventario,
                Producto.nombre.label('nombre_producto'),
                Producto.codigo_producto.label('codigo_producto'),
                Sucursal.nombre.label('nombre_sucursal'),
                Proveedor.nombre.label('nombre_proveedor')
            )
            .select_from(Alert)
            .join(Inventario, Alert.id_inventario == Inventario.id_inventario)
            .join(Producto, Inventario.id_producto == Producto.id_producto)
            .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
            .join(Sucursal, Ubicacion.id_sucursal == Sucursal.id_sucursal)
            .join(Proveedor, Producto.id_proveedor == Proveedor.id_proveedor)
        )

        # Filtrar por sucursal
        if filter_params.id_sucursal is not None:
            query = query.filter(Sucursal.id_sucursal == filter_params.id_sucursal)
        
        # Filtrar por mes (formato YYYY-MM)
        if filter_params.mes:
            try:
                year, month = map(int, filter_params.mes.split('-'))
                query = query.filter(
                    and_(
                        extract('year', Alert.fecha_alerta) == year,
                        extract('month', Alert.fecha_alerta) == month
                    )
                )
            except (ValueError, AttributeError):
                # Si el formato no es correcto, ignoramos este filtro
                pass

        # Filtrar por estado
        if filter_params.estado:
            query = query.filter(Alert.estado == filter_params.estado)

        # Ordenar por fecha (más recientes primero)
        query = query.order_by(Alert.fecha_alerta.desc())

        results = query.all()

        # Convertir los resultados al formato deseado
        alerts = []
        for alert, inv, nombre_producto, codigo_producto, nombre_sucursal, nombre_proveedor in results:
            alert_dict = {
                "id_alerta": alert.id_alerta,
                "id_inventario": alert.id_inventario,
                "fecha_alerta": alert.fecha_alerta,
                "cantidad_actual": alert.cantidad_actual,
                "estado": alert.estado,
                "observacion": alert.observacion,
                "nombre_producto": nombre_producto,
                "codigo_producto": codigo_producto,
                "nombre_sucursal": nombre_sucursal,
                "nombre_proveedor": nombre_proveedor
            }
            alerts.append(alert_dict)

        return alerts

    def update_alert_status(self, alert_id: int, new_status: AlertStatus) -> Optional[Alert]:
        """Actualiza el estado de una alerta"""
        alert = self.db.query(Alert).filter(Alert.id_alerta == alert_id).first()
        if alert:
            self.db.query(Alert).filter(Alert.id_alerta == alert_id).update({
                "estado": new_status.value
            })
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def get_alert_history(self, pagina: int = 1, limite: int = 10) -> dict:
        """
        Obtiene el historial de alertas ordenado por fecha con paginación
        """
        # Calcular el offset basado en la página y límite
        offset = (pagina - 1) * limite

        # Consulta base
        base_query = (
            self.db.query(
                Alert,
                Inventario,
                Producto.nombre.label('nombre_producto'),
                Producto.codigo_producto.label('codigo_producto'),
                Sucursal.nombre.label('nombre_sucursal'),
                Proveedor.nombre.label('nombre_proveedor')
            )
            .select_from(Alert)
            .join(Inventario, Alert.id_inventario == Inventario.id_inventario)
            .join(Producto, Inventario.id_producto == Producto.id_producto)
            .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
            .join(Sucursal, Ubicacion.id_sucursal == Sucursal.id_sucursal)
            .join(Proveedor, Producto.id_proveedor == Proveedor.id_proveedor)
            .order_by(Alert.fecha_alerta.desc())
        )

        # Obtener el total de registros
        total = base_query.count()

        # Aplicar paginación
        results = base_query.offset(offset).limit(limite).all()

        # Convertir los resultados al formato deseado
        alerts = []
        for alert, inv, nombre_producto, codigo_producto, nombre_sucursal, nombre_proveedor in results:
            alert_dict = {
                "id_alerta": alert.id_alerta,
                "id_inventario": alert.id_inventario,
                "fecha_alerta": alert.fecha_alerta,
                "cantidad_actual": alert.cantidad_actual,
                "estado": alert.estado,
                "observacion": alert.observacion,
                "nombre_producto": nombre_producto,
                "codigo_producto": codigo_producto,
                "nombre_sucursal": nombre_sucursal,
                "nombre_proveedor": nombre_proveedor
            }
            alerts.append(alert_dict)

        # Calcular el total de páginas
        total_paginas = (total + limite - 1) // limite

        return {
            "alertas": alerts,
            "total": total,
            "pagina_actual": pagina,
            "total_paginas": total_paginas,
            "elementos_por_pagina": limite
        }

    def check_inventory_alerts(self) -> List[Alert]:
        """
        Verifica el inventario y genera alertas según las condiciones
        """
        alerts = []
        # Verificar inventario
        inventory_query = (
            self.db.query(
                Inventario.id_inventario,
                Inventario.cantidad_actual.label('cantidad'),
                Inventario.stock_minimo.label('minimo')
            )
            .filter(Inventario.cantidad_actual <= Inventario.stock_minimo)
            .all()
        )

        for inv in inventory_query:
            # Determinar si es stock mínimo o stock bajo (70% del stock mínimo)
            cantidad_actual = float(inv.cantidad)
            stock_minimo = float(inv.minimo)
            is_critical = cantidad_actual <= (stock_minimo * 0.7)
            estado = AlertStatus.STOCK_BAJO.value if is_critical else AlertStatus.STOCK_MINIMO.value
            
            # Crear alerta
            alert = Alert(
                id_inventario=inv.id_inventario,
                fecha_alerta=datetime.now(),
                cantidad_actual=cantidad_actual,
                estado=estado,
                observacion=f"{'Stock bajo' if is_critical else 'Stock mínimo'} - Cantidad actual: {cantidad_actual:.2f}"
            )
            self.db.add(alert)
            alerts.append(alert)
        
        self.db.commit()
        return alerts