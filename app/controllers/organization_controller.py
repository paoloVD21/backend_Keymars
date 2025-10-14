from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.organization_service import OrganizationService
from app.schemas.organization_schemas import RolResponse, SucursalResponse
from typing import List

class OrganizationController:
    def __init__(self, db: Session):
        self.db = db

    def get_roles(self) -> List[RolResponse]:
        """
        Endpoint para obtener la lista de roles (solo id y nombre)
        """
        roles = OrganizationService.get_roles(self.db)
        return [RolResponse.model_validate({
            'id_rol': rol.id_rol,
            'nombre': rol.nombre
        }) for rol in roles]

    def get_sucursales(self) -> List[SucursalResponse]:
        """
        Endpoint para obtener la lista de sucursales (solo id y nombre)
        """
        sucursales = OrganizationService.get_sucursales(self.db)
        return [SucursalResponse.model_validate({
            'id_sucursal': sucursal.id_sucursal,
            'nombre': sucursal.nombre
        }) for sucursal in sucursales]