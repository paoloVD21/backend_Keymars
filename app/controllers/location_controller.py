from fastapi import Depends
from sqlalchemy.orm import Session
from app.services.location_service import LocationService
from app.schemas import location_schemas
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.models import Usuario
from typing import List

class LocationController:
    @staticmethod
    async def get_locations_by_branch(
        branch_id: int,
        db: Session,
        current_user: Usuario
    ) -> List[location_schemas.LocationResponse]:
        """
        Obtiene todas las ubicaciones activas de una sucursal
        """
        service = LocationService(db)
        return service.get_locations_by_branch(branch_id=branch_id)

    @staticmethod
    async def create_location(
        location_data: location_schemas.LocationCreate,
        db: Session,
        current_user: Usuario
    ) -> location_schemas.LocationResponse:
        """
        Crea una nueva ubicación
        """
        service = LocationService(db)
        return service.create_location(location_data=location_data)