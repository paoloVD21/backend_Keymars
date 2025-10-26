from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Ubicacion, Sucursal
from app.schemas import location_schemas
from typing import List
from fastapi import HTTPException

class LocationService:
    def __init__(self, db: Session):
        self.db = db

    def get_locations_by_branch(self, branch_id: int) -> List[location_schemas.LocationResponse]:
        """
        Obtiene todas las ubicaciones activas de una sucursal
        """
        db_locations = self.db.query(Ubicacion).filter(
            and_(
                Ubicacion.id_sucursal == branch_id,
                Ubicacion.activo == True
            )
        ).all()
        
        # Convertir los modelos SQLAlchemy a esquemas Pydantic
        return [location_schemas.LocationResponse.from_orm(location) for location in db_locations]

    def create_location(self, location_data: location_schemas.LocationCreate) -> location_schemas.LocationResponse:
        """
        Crea una nueva ubicación
        """
        # Verificar que existe la sucursal y está activa
        sucursal = self.db.query(Sucursal).filter(
            and_(
                Sucursal.id_sucursal == location_data.id_sucursal,
                Sucursal.activo == True
            )
        ).first()
        if not sucursal:
            raise HTTPException(status_code=400, detail="Sucursal no válida o inactiva")

        # Verificar que el código de ubicación no exista en la misma sucursal
        existing_location = self.db.query(Ubicacion).filter(
            and_(
                Ubicacion.codigo_ubicacion == location_data.codigo_ubicacion,
                Ubicacion.id_sucursal == location_data.id_sucursal,
                Ubicacion.activo == True
            )
        ).first()
        if existing_location:
            raise HTTPException(status_code=400, detail="Ya existe una ubicación con ese código en esta sucursal")

        # Verificar que el tipo de ubicación sea válido
        tipos_validos = ['ESTANTERIA', 'REFRIGERADO', 'SECO', 'LIQUIDOS', 'OTROS']
        if location_data.tipo_ubicacion.upper() not in tipos_validos:
            raise HTTPException(status_code=400, detail="Tipo de ubicación no válido")

        # Crear la nueva ubicación
        new_location = Ubicacion(
            nombre=location_data.nombre,
            codigo_ubicacion=location_data.codigo_ubicacion.upper(),
            tipo_ubicacion=location_data.tipo_ubicacion.upper(),
            id_sucursal=location_data.id_sucursal
        )
        
        try:
            self.db.add(new_location)
            self.db.commit()
            self.db.refresh(new_location)
            return location_schemas.LocationResponse.from_orm(new_location)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear la ubicación")