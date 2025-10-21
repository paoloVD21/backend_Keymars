from sqlalchemy.orm import Session
from app.models.inventory_models import (
    Producto, Categoria, Marca, Proveedor, Inventario,
    producto_proveedor
)
from app.schemas import product_schemas
from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy import or_

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_products(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> dict:
        query = (
            self.db.query(
                Producto,
                Categoria.nombre.label('categoria_nombre'),
                Marca.nombre.label('marca_nombre'),
                Proveedor.nombre.label('proveedor_nombre'),
                Inventario.cantidad_actual
            )
            .join(Categoria, Producto.id_categoria == Categoria.id_categoria)
            .outerjoin(Marca, Producto.id_marca == Marca.id_marca)
            .join(producto_proveedor, Producto.id_producto == producto_proveedor.c.id_producto)
            .join(Proveedor, producto_proveedor.c.id_proveedor == Proveedor.id_proveedor)
            .outerjoin(Inventario, Producto.id_producto == Inventario.id_producto)
        )

        # Aplicar filtros de búsqueda
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    Producto.codigo_producto.ilike(search),
                    Producto.nombre.ilike(search),
                    Categoria.nombre.ilike(search)
                )
            )

        # Filtrar por estado activo
        if activo is not None:
            query = query.filter(Producto.activo == activo)

        # Obtener total de registros
        total = query.count()
        
        # Aplicar paginación
        results = query.offset(skip).limit(limit).all()

        # Procesar resultados
        products = []
        for result in results:
            product_dict = result[0].__dict__
            product_dict.update({
                'categoria_nombre': result[1],
                'marca_nombre': result[2],
                'proveedor_nombre': result[3],
                'stock_actual': result[4] or 0
            })
            products.append(product_dict)

        return {
            "total": total,
            "items": products
        }

    def create_product(self, product: product_schemas.ProductCreate) -> Producto:
        # Verificar que existe la categoría
        if not self.db.query(Categoria).filter(Categoria.id_categoria == product.id_categoria).first():
            raise HTTPException(status_code=400, detail="Categoría no encontrada")
        
        # Verificar que existe la marca si se proporciona
        if product.id_marca and not self.db.query(Marca).filter(Marca.id_marca == product.id_marca).first():
            raise HTTPException(status_code=400, detail="Marca no encontrada")
        
        # Verificar que existe el proveedor
        if not self.db.query(Proveedor).filter(Proveedor.id_proveedor == product.id_proveedor).first():
            raise HTTPException(status_code=400, detail="Proveedor no encontrado")

        # Verificar que el código de producto no exista
        if self.db.query(Producto).filter(Producto.codigo_producto == product.codigo_producto).first():
            raise HTTPException(status_code=400, detail="El código de producto ya existe")

        # Extraer id_proveedor del modelo para manejar la relación many-to-many
        proveedor_id = product.id_proveedor
        product_data = product.model_dump(exclude={'id_proveedor'})
        
        db_product = Producto(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        # Asociar el proveedor al producto
        proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == proveedor_id).first()
        db_product.proveedores.append(proveedor)

        # Crear registro inicial en inventario
        inventario = Inventario(
            id_producto=db_product.id_producto,
            cantidad_actual=0
        )
        self.db.add(inventario)
        self.db.commit()

        return db_product

    def get_product_by_id(self, product_id: int) -> Producto:
        product = self.db.query(Producto).filter(Producto.id_producto == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product

    def update_product(self, product_id: int, product_data: product_schemas.ProductUpdate) -> Producto:
        db_product = self.get_product_by_id(product_id)
        
        # Verificar que existe la categoría
        if not self.db.query(Categoria).filter(Categoria.id_categoria == product_data.id_categoria).first():
            raise HTTPException(status_code=400, detail="Categoría no encontrada")
        
        # Verificar que existe la marca si se proporciona
        if product_data.id_marca and not self.db.query(Marca).filter(Marca.id_marca == product_data.id_marca).first():
            raise HTTPException(status_code=400, detail="Marca no encontrada")
        
        # Verificar que existe el proveedor
        proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == product_data.id_proveedor).first()
        if not proveedor:
            raise HTTPException(status_code=400, detail="Proveedor no encontrado")

        # Verificar que el código de producto no exista (si se está cambiando)
        if (product_data.codigo_producto != db_product.codigo_producto and
            self.db.query(Producto).filter(Producto.codigo_producto == product_data.codigo_producto).first()):
            raise HTTPException(status_code=400, detail="El código de producto ya existe")

        # Extraer id_proveedor del modelo para manejar la relación many-to-many
        proveedor_id = product_data.id_proveedor
        update_data = product_data.model_dump(exclude={'id_proveedor'})

        # Actualizar campos básicos del producto
        for key, value in update_data.items():
            setattr(db_product, key, value)

        # Actualizar la relación con el proveedor
        db_product.proveedores = [proveedor]

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def toggle_product_status(self, product_id: int) -> Producto:
        # Actualizar directamente usando update()
        current_status = self.db.query(Producto.activo).filter(Producto.id_producto == product_id).scalar()
        new_status = not bool(current_status)
        
        self.db.query(Producto).filter(Producto.id_producto == product_id).update(
            {"activo": new_status},
            synchronize_session=False
        )
        self.db.commit()
        
        # Obtener el producto actualizado
        return self.get_product_by_id(product_id)

    @staticmethod
    def get_productos_activos(db: Session) -> List[Producto]:
        """
        Obtiene todos los productos activos para selectores/modales
        """
        return db.query(Producto).filter(Producto.activo == True).all()