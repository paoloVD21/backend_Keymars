from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.supplier_service import SupplierService
from app.schemas import supplier_schemas
from typing import List, Optional

class SupplierController:
    def __init__(self, db: Session):
        self.db = db
        self.service = SupplierService(db)

    def get_proveedores_activos(self) -> List[supplier_schemas.SupplierModal]:
        """
        Endpoint para obtener la lista de proveedores activos (solo id y nombre)
        """
        proveedores = SupplierService.get_proveedores_activos(self.db)
        return [supplier_schemas.SupplierModal.model_validate({
            'id_proveedor': proveedor.id_proveedor,
            'nombre': proveedor.nombre
        }) for proveedor in proveedores]

    @staticmethod
    async def get_suppliers(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        search: Optional[str] = None,
        activo: Optional[bool] = None,
        db: Session = Depends(get_db)
    ) -> supplier_schemas.SupplierList:
        """
        Obtiene la lista paginada de proveedores con filtros opcionales.
        """
        service = SupplierService(db)
        result = service.get_suppliers(skip=skip,
            limit=limit,
            search=search,
            activo=activo
        )
        supplier_responses = [supplier_schemas.SupplierResponse.model_validate(proveedor) for proveedor in result["items"]]
        return supplier_schemas.SupplierList(total=result["total"], proveedores=supplier_responses)

    @staticmethod
    async def create_supplier(
        supplier_data: supplier_schemas.SupplierCreate,
        db: Session = Depends(get_db)
    ) -> supplier_schemas.SupplierResponse:
        service = SupplierService(db)
        return service.create_supplier(supplier_data)

    @staticmethod
    async def get_supplier(
        supplier_id: int,
        db: Session = Depends(get_db)
    ) -> supplier_schemas.SupplierResponse:
        service = SupplierService(db)
        return service.get_supplier_by_id(supplier_id)

    @staticmethod
    async def update_supplier(
        supplier_id: int,
        supplier_data: supplier_schemas.SupplierUpdate,
        db: Session = Depends(get_db)
    ) -> supplier_schemas.SupplierResponse:
        service = SupplierService(db)
        return service.update_supplier(supplier_id, supplier_data)

    @staticmethod
    async def toggle_supplier_status(
        supplier_id: int,
        db: Session = Depends(get_db)
    ) -> supplier_schemas.SupplierResponse:
        service = SupplierService(db)
        return service.toggle_supplier_status(supplier_id)