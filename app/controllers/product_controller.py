from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.product_service import ProductService
from app.schemas import product_schemas
from typing import List, Optional

class ProductController:
    def __init__(self, db: Session):
        self.db = db
        self.service = ProductService(db)

    def get_productos_activos(self) -> List[product_schemas.ProductModal]:
        """
        Obtiene la lista de productos activos para selector/modal
        """
        productos = ProductService.get_productos_activos(self.db)
        return [product_schemas.ProductModal.model_validate({
            'id_producto': producto.id_producto,
            'nombre': producto.nombre,
            'codigo_producto': producto.codigo_producto
        }) for producto in productos]

    async def get_products(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        search: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> product_schemas.ProductList:
        """
        Obtiene la lista paginada de productos con filtros opcionales
        """
        result = self.service.get_products(skip, limit, search, activo)
        product_responses = [
            product_schemas.ProductResponse.model_validate(product) 
            for product in result["items"]
        ]
        return product_schemas.ProductList(total=result["total"], productos=product_responses)

    async def create_product(
        self, 
        product_data: product_schemas.ProductCreate
    ) -> product_schemas.ProductResponse:
        product = self.service.create_product(product_data)
        return product_schemas.ProductResponse.model_validate(product)

    async def get_product(
        self,
        product_id: int
    ) -> product_schemas.ProductResponse:
        product = self.service.get_product_by_id(product_id)
        return product_schemas.ProductResponse.model_validate(product)

    async def update_product(
        self,
        product_id: int,
        product_data: product_schemas.ProductUpdate
    ) -> product_schemas.ProductResponse:
        product = self.service.update_product(product_id, product_data)
        return product_schemas.ProductResponse.model_validate(product)

    async def toggle_product_status(
        self,
        product_id: int
    ) -> product_schemas.ProductResponse:
        product = self.service.toggle_product_status(product_id)
        return product_schemas.ProductResponse.model_validate(product)