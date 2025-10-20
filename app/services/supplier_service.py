from sqlalchemy.orm import Session
from app.models.inventory_models import Proveedor
from app.schemas.supplier_schemas import SupplierCreate, SupplierUpdate
from fastapi import HTTPException
from typing import Optional, List

class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    def get_suppliers(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> dict:
        query = self.db.query(Proveedor)

        # Aplicar filtros de búsqueda
        if search:
            search = f"%{search}%"
            query = query.filter(
                (Proveedor.nombre.ilike(search)) |
                (Proveedor.email.ilike(search)) |
                (Proveedor.telefono.ilike(search))
            )

        # Filtrar por estado activo
        if activo is not None:
            query = query.filter(Proveedor.activo == activo)

        # Obtener total de registros
        total = query.count()
        
        # Aplicar paginación
        items = query.offset(skip).limit(limit).all()

        return {
            "total": total,
            "items": items
        }

    def create_supplier(self, supplier: SupplierCreate) -> Proveedor:
        db_supplier = Proveedor(**supplier.model_dump())
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def get_supplier_by_id(self, supplier_id: int) -> Proveedor:
        supplier = self.db.query(Proveedor).filter(Proveedor.id_proveedor == supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return supplier

    def update_supplier(self, supplier_id: int, supplier_data: SupplierUpdate) -> Proveedor:
        db_supplier = self.get_supplier_by_id(supplier_id)
        
        for key, value in supplier_data.model_dump().items():
            setattr(db_supplier, key, value)

        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def toggle_supplier_status(self, supplier_id: int) -> Proveedor:
        supplier = self.get_supplier_by_id(supplier_id)
        current_status = self.db.query(Proveedor.activo).filter(Proveedor.id_proveedor == supplier_id).scalar()
        # Usamos la función update() de SQLAlchemy para actualizar el estado
        self.db.query(Proveedor).filter(Proveedor.id_proveedor == supplier_id).update(
            {"activo": not bool(current_status)}, synchronize_session=False
        )
        self.db.commit()
        self.db.refresh(supplier)
        return supplier