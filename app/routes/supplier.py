from fastapi import APIRouter, Depends, Query
from app.controllers.supplier_controller import SupplierController
from app.schemas import supplier_schemas
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import verify_token

router = APIRouter(
    prefix="/api/suppliers",
    tags=["suppliers"]
)

@router.get("/ListarProveedores", response_model=supplier_schemas.SupplierList)
async def get_suppliers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(None),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista paginada de proveedores.
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **search**: Término de búsqueda (nombre, email o teléfono)
    - **activo**: Filtrar por estado del proveedor
    """
    result = await SupplierController.get_suppliers(
        skip=skip,
        limit=limit,
        search=search,
        activo=activo,
        db=db
    )
    return result

@router.post("/crearProveedor", response_model=supplier_schemas.SupplierResponse)
async def create_supplier(
    supplier_data: supplier_schemas.SupplierCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Crea un nuevo proveedor.
    """

    return await SupplierController.create_supplier(supplier_data=supplier_data, db=db)

@router.get("/obtenerProveedor/{supplier_id}", response_model=supplier_schemas.SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene los detalles de un proveedor específico.
    """
    controller = SupplierController()
    return controller.get_supplier(supplier_id, db)

@router.put("/actualizarProveedor/{supplier_id}", response_model=supplier_schemas.SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: supplier_schemas.SupplierUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Actualiza los datos de un proveedor existente.
    """
    controller = SupplierController()
    return controller.update_supplier(supplier_id, supplier_data, db)

@router.patch("/cambiarEstadoProveedor/{supplier_id}", response_model=supplier_schemas.SupplierResponse)
def toggle_supplier_status(
    supplier_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Activa o desactiva un proveedor.
    """
    controller = SupplierController()
    return controller.toggle_supplier_status(supplier_id, db)