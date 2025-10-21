from fastapi import APIRouter, Depends, Query
from app.controllers.product_controller import ProductController
from app.schemas import product_schemas
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import verify_token

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("/listarModalProductos", response_model=List[product_schemas.ProductModal])
def get_productos_activos(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista de productos activos para selector/modal
    """
    controller = ProductController(db)
    return controller.get_productos_activos()

@router.get("/ListarProductos", response_model=product_schemas.ProductList)
async def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Buscar por código, nombre o categoría"),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene la lista paginada de productos.
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **search**: Término de búsqueda (código, nombre o categoría)
    - **activo**: Filtrar por estado del producto
    """
    controller = ProductController(db)
    return await controller.get_products(skip=skip, limit=limit, search=search, activo=activo)

@router.post("/crearProducto", response_model=product_schemas.ProductResponse)
async def create_product(
    product_data: product_schemas.ProductCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Crea un nuevo producto.
    """
    controller = ProductController(db)
    return await controller.create_product(product_data=product_data)

@router.get("/obtenerProducto/{product_id}", response_model=product_schemas.ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Obtiene los detalles de un producto específico.
    """
    controller = ProductController(db)
    return await controller.get_product(product_id)

@router.put("/actualizarProducto/{product_id}", response_model=product_schemas.ProductResponse)
async def update_product(
    product_id: int,
    product_data: product_schemas.ProductUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Actualiza los datos de un producto existente.
    """
    controller = ProductController(db)
    return await controller.update_product(product_id, product_data)

@router.patch("/cambiarEstadoProducto/{product_id}", response_model=product_schemas.ProductResponse)
async def toggle_product_status(
    product_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Activa o desactiva un producto.
    """
    controller = ProductController(db)
    return await controller.toggle_product_status(product_id)