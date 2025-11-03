from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard_schemas import (
    DashboardStats,
    MovimientosData,
    DistribucionData
)

class DashboardController:
    def __init__(self, db: Session):
        self.service = DashboardService(db)

    def get_stats(self) -> DashboardStats:
        """
        Obtiene estadísticas generales del dashboard
        """
        return DashboardStats.model_validate(self.service.get_general_stats())

    def get_movimientos(self) -> MovimientosData:
        """
        Obtiene estadísticas de movimientos mensuales
        """
        return MovimientosData.model_validate(self.service.get_movimientos_mensuales())

    def get_distribucion(self) -> DistribucionData:
        """
        Obtiene la distribución de productos por categoría
        """
        return DistribucionData.model_validate(self.service.get_distribucion_categorias())