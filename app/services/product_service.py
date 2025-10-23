from sqlalchemy.orm import Session
from app.models.inventory_models import (
    Producto, Categoria, Marca, Proveedor, Inventario, PrecioProducto,
    producto_proveedor
)
from app.schemas import product_schemas
from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy import or_
from decimal import Decimal
from datetime import datetime

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
        # Primero obtenemos los IDs de los productos de manera distinta
        product_ids_query = (
            self.db.query(Producto.id_producto)
            .join(Categoria)
            .outerjoin(Marca)
            .outerjoin(producto_proveedor)
            .outerjoin(Proveedor)
            .outerjoin(Inventario)
        )

        # Aplicar filtros de búsqueda
        if search:
            search = f"%{search}%"
            product_ids_query = product_ids_query.filter(
                or_(
                    Producto.codigo_producto.ilike(search),
                    Producto.nombre.ilike(search),
                    Categoria.nombre.ilike(search)
                )
            )

        # Filtrar por estado activo
        if activo is not None:
            product_ids_query = product_ids_query.filter(Producto.activo == activo)

        # Obtener IDs únicos con paginación
        product_ids = product_ids_query.distinct().offset(skip).limit(limit).all()
        
        # Obtener total de registros únicos
        total = product_ids_query.distinct().count()
        
        # Ahora obtenemos los detalles completos solo para los IDs seleccionados
        results = []
        for (pid,) in product_ids:
            result = (
                self.db.query(
                    Producto,
                    Categoria.nombre.label('categoria_nombre'),
                    Marca.nombre.label('marca_nombre'),
                    Proveedor.nombre.label('proveedor_nombre'),
                    Inventario.cantidad_actual
                )
                .join(Categoria, Producto.id_categoria == Categoria.id_categoria)
                .outerjoin(Marca, Producto.id_marca == Marca.id_marca)
                .outerjoin(producto_proveedor, Producto.id_producto == producto_proveedor.c.id_producto)
                .outerjoin(Proveedor, producto_proveedor.c.id_proveedor == Proveedor.id_proveedor)
                .outerjoin(Inventario, Producto.id_producto == Inventario.id_producto)
                .filter(Producto.id_producto == pid)
                .first()
            )
            if result:
                results.append(result)

        # Procesar resultados
        products = []
        for result in results:
            if result and result[0]:  # Verificamos que result y su primer elemento no sean None
                product_dict = result[0].__dict__
                product_dict.update({
                    'categoria_nombre': result[1],
                    'marca_nombre': result[2],
                    'proveedor_nombre': result[3] if result[3] else None,
                    'stock_actual': result[4] if result[4] is not None else 0
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

        # Extraer campos que van en otras tablas
        proveedor_id = product.id_proveedor
        precio = product.precio
        product_data = product.model_dump(exclude={'id_proveedor', 'precio', 'stock_minimo'})
        
        # Crear el producto
        db_product = Producto(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        # Asociar el proveedor al producto
        proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == proveedor_id).first()
        db_product.proveedores.append(proveedor)

        # Crear precio inicial
        precio_producto = PrecioProducto(
            id_producto=db_product.id_producto,
            precio=precio
        )
        self.db.add(precio_producto)

        # Crear registro inicial en inventario
        inventario = Inventario(
            id_producto=db_product.id_producto,
            cantidad_actual=0,
            stock_minimo=product.stock_minimo
        )
        self.db.add(inventario)
        self.db.commit()

        return db_product

    def get_product_by_id(self, product_id: int) -> dict:
        """
        Obtiene un producto por su ID incluyendo todos los campos necesarios para ProductResponse
        """
        result = (
            self.db.query(
                Producto,
                Categoria.nombre.label('categoria_nombre'),
                Marca.nombre.label('marca_nombre'),
                Proveedor.nombre.label('proveedor_nombre'),
                Inventario.cantidad_actual,
                Inventario.stock_minimo,
                PrecioProducto.precio
            )
            .join(Categoria, Producto.id_categoria == Categoria.id_categoria)
            .outerjoin(Marca, Producto.id_marca == Marca.id_marca)
            .join(producto_proveedor, Producto.id_producto == producto_proveedor.c.id_producto)
            .join(Proveedor, producto_proveedor.c.id_proveedor == Proveedor.id_proveedor)
            .outerjoin(Inventario, Producto.id_producto == Inventario.id_producto)
            .outerjoin(
                PrecioProducto,
                (Producto.id_producto == PrecioProducto.id_producto) &
                (PrecioProducto.fecha_fin.is_(None))
            )
            .filter(Producto.id_producto == product_id)
            .first()
        )

        if not result:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        product_dict = result[0].__dict__
        product_dict.update({
            'categoria_nombre': result[1],
            'marca_nombre': result[2],
            'proveedor_nombre': result[3],
            'stock_actual': result[4] or Decimal('0'),
            'stock_minimo': result[5] or Decimal('0'),
            'precio': result[6] or Decimal('0')
        })

        return product_dict

    def update_product(self, product_id: int, product_data: product_schemas.ProductUpdate) -> dict:
        # Verificar que existe el producto
        product = self.db.query(Producto).filter(Producto.id_producto == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
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
        if (product_data.codigo_producto != product.codigo_producto and
            self.db.query(Producto).filter(Producto.codigo_producto == product_data.codigo_producto).first()):
            raise HTTPException(status_code=400, detail="El código de producto ya existe")

        # Extraer campos que van en otras tablas
        proveedor_id = product_data.id_proveedor
        precio = product_data.precio
        update_data = product_data.model_dump(exclude={'id_proveedor', 'precio', 'stock_minimo'})

        # Actualizar campos básicos del producto
        for key, value in update_data.items():
            setattr(product, key, value)

        # Actualizar la relación con el proveedor
        product.proveedores = [proveedor]

        # Actualizar precio si ha cambiado
        current_price = (
            self.db.query(PrecioProducto.precio)
            .filter(PrecioProducto.id_producto == product_id)
            .filter(PrecioProducto.fecha_fin.is_(None))
            .scalar()
        )
        
        if current_price != precio:
            # Cerrar precio actual
            self.db.query(PrecioProducto).filter(
                PrecioProducto.id_producto == product_id,
                PrecioProducto.fecha_fin.is_(None)
            ).update({"fecha_fin": datetime.utcnow()})
            
            # Crear nuevo precio
            nuevo_precio = PrecioProducto(
                id_producto=product_id,
                precio=precio
            )
            self.db.add(nuevo_precio)

        # Actualizar stock_minimo en inventario
        self.db.query(Inventario).filter(
            Inventario.id_producto == product_id
        ).update({"stock_minimo": product_data.stock_minimo})

        self.db.commit()
        self.db.refresh(product)

        return self.get_product_by_id(product_id)

    def toggle_product_status(self, product_id: int) -> dict:
        # Verificar que existe el producto y obtenerlo
        product = self.db.query(Producto).filter(Producto.id_producto == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Cambiar el estado directamente en la base de datos
        current_status = self.db.query(Producto.activo).filter(Producto.id_producto == product_id).scalar()
        new_status = not bool(current_status)
        
        # Actualizar usando el objeto de la sesión actual
        self.db.query(Producto).filter(Producto.id_producto == product_id).update(
            {"activo": new_status},
            synchronize_session="fetch"
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