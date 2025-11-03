from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.controllers.dashboard_controller import DashboardController
from app.schemas.dashboard_schemas import (
    DashboardStats,
    MovimientosData,
    DistribucionData
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)

def get_controller(db: Session = Depends(get_db)) -> DashboardController:
    return DashboardController(db)

@router.get("/stats", response_model=DashboardStats)
@router.get("/estadisticas", response_model=DashboardStats)
async def get_dashboard_stats(
    controller: DashboardController = Depends(get_controller),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas generales para el dashboard:
    - Total de productos activos
    - Stock total disponible
    - Total de proveedores activos
    - Tendencias de crecimiento/decrecimiento
    """
    return controller.get_stats()

@router.get("/movimientos", response_model=MovimientosData)
async def get_dashboard_movimientos(
    controller: DashboardController = Depends(get_controller),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de movimientos mensuales:
    - Etiquetas de meses
    - Cantidad de entradas por mes
    - Cantidad de salidas por mes
    """
    return controller.get_movimientos()

@router.get("/distribucion", response_model=DistribucionData)
async def get_dashboard_distribucion(
    controller: DashboardController = Depends(get_controller),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene la distribución de productos por categoría:
    - Nombres de categorías
    - Cantidad de productos en cada categoría
    """
    return controller.get_distribucion()