from sqlalchemy.orm import Session
from app.models.organization_models import Rol, Sucursal
from typing import List

class OrganizationService:
    @staticmethod
    def get_roles(db: Session) -> List[Rol]:
        """
        Obtiene la lista de roles activos
        """
        return db.query(Rol).filter(Rol.activo == True).all()

    @staticmethod
    def get_sucursales(db: Session) -> List[Sucursal]:
        """
        Obtiene la lista de sucursales activas
        """
        return db.query(Sucursal).filter(Sucursal.activo == True).all()