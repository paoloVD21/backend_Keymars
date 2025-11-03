from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.alert_schemas import Alert, AlertUpdate, AlertFilter, AlertHistoryResponse
from app.services.alert_service import AlertService
from fastapi import Query

router = APIRouter(
    prefix="/api/alertas",
    tags=["alertas"]
)

@router.get("/historial", response_model=AlertHistoryResponse)
async def get_alert_history(
    pagina: int = Query(1, description="Número de página"),
    limite: int = Query(10, description="Número de elementos por página"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene el historial de alertas ordenado por fecha (más recientes primero)
    con paginación.
    """
    alert_service = AlertService(db)
    return alert_service.get_alert_history(pagina=pagina, limite=limite)

@router.post("/filtrar", response_model=List[Alert])
async def filter_alerts(
    filter_params: AlertFilter,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtiene la lista de alertas aplicando los filtros especificados
    
    Filtros disponibles:
    - Inventario
    - Mes/Año
    - Estado
    """
    alert_service = AlertService(db)
    return alert_service.get_alerts_with_filter(filter_params)

@router.patch("/{alert_id}", response_model=Alert)
async def update_alert_status(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualiza el estado de una alerta
    """
    alert_service = AlertService(db)
    alert = alert_service.update_alert_status(alert_id, alert_update.estado)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alert

@router.get("/check")
async def check_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Verifica el inventario y genera alertas según sea necesario
    """
    alert_service = AlertService(db)
    return alert_service.check_inventory_alerts()