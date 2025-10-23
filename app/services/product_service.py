import logging
from sqlalchemy.orm import Session
from app.models.inventory_models import (
    Producto, Categoria, Marca, Proveedor, Inventario, PrecioProducto,
    Ubicacion
)
from app.schemas import product_schemas
from fastapi import HTTPException

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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
        # Consulta actualizada sin la tabla intermedia producto_proveedor
        product_ids_query = (
            self.db.query(Producto.id_producto)
            .join(Categoria)
            .outerjoin(Marca)
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
                    Inventario.cantidad_actual,
                    Inventario.stock_minimo,
                    PrecioProducto.precio
                )
                .join(Categoria, Producto.id_categoria == Categoria.id_categoria)
                .outerjoin(Marca, Producto.id_marca == Marca.id_marca)
                .outerjoin(Proveedor, Producto.id_proveedor == Proveedor.id_proveedor)
                .outerjoin(Inventario, Producto.id_producto == Inventario.id_producto)
                .outerjoin(
                    PrecioProducto,
                    (Producto.id_producto == PrecioProducto.id_producto) &
                    (PrecioProducto.fecha_fin.is_(None))
                )
                .filter(Producto.id_producto == pid)
                .first()
            )
            if result:
                results.append(result)

        # Procesar resultados
        products = []
        for result in results:
            if result and result[0]:  # Verificamos que result y su primer elemento no sean None
                product = result[0]
                product_dict = {
                    'id_producto': product.id_producto,
                    'codigo_producto': product.codigo_producto,
                    'nombre': product.nombre,
                    'descripcion': product.descripcion,
                    'id_categoria': product.id_categoria,
                    'id_marca': product.id_marca,
                    'unidad_medida': product.unidad_medida,
                    'activo': product.activo,
                    'fecha_creacion': product.fecha_creacion,
                    'categoria_nombre': result[1] or "",  # Asegurarnos de que nunca sea None
                    'marca_nombre': result[2],
                    'proveedor_nombre': result[3],
                    'stock_actual': Decimal(str(result[4])) if result[4] is not None else Decimal('0'),
                    'stock_minimo': Decimal(str(result[5])) if result[5] is not None else Decimal('0'),
                    'precio': Decimal(str(result[6])) if result[6] is not None else Decimal('0')
                }
                products.append(product_dict)
                
        return {
            "total": total,
            "items": products
        }

    def create_product(self, product: product_schemas.ProductCreate) -> dict:
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

        # Preparar los datos del producto
        product_data = product.model_dump(
            exclude={'precio', 'stock_minimo'}
        )
        
        # Obtener el nombre de la categoría
        categoria = self.db.query(Categoria).filter(Categoria.id_categoria == product.id_categoria).first()
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoría no encontrada")

        # Obtener marca si se proporciona
        marca_nombre = None
        if product.id_marca is not None:
            marca = self.db.query(Marca).filter(Marca.id_marca == product.id_marca).first()
            marca_nombre = marca.nombre if marca else None

        # Obtener el proveedor
        proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == product.id_proveedor).first()
        if not proveedor:
            raise HTTPException(status_code=400, detail="Proveedor no encontrado")
        
        # Crear el producto - id_proveedor ya está incluido en product_data
        db_product = Producto(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        # Crear precio inicial
        precio_producto = PrecioProducto(
            id_producto=db_product.id_producto,
            precio=product.precio
        )
        self.db.add(precio_producto)

        # Crear registro inicial en inventario
        # Buscar una ubicación por defecto (primera ubicación activa)
        ubicacion_default = self.db.query(Ubicacion).filter(Ubicacion.activo == True).first()
        if not ubicacion_default:
            raise HTTPException(status_code=400, detail="No hay ubicaciones disponibles para el inventario")
                
        inventario = Inventario(
            id_producto=db_product.id_producto,
            id_ubicacion=ubicacion_default.id_ubicacion,
            cantidad_actual=0,
            stock_minimo=product.stock_minimo
        )
        self.db.add(inventario)
            
        self.db.commit()
        self.db.refresh(db_product)

        # Construir respuesta con todos los campos necesarios
        result = self.db.query(
            Producto,
            Categoria.nombre.label('categoria_nombre'),
            Marca.nombre.label('marca_nombre'),
            Proveedor.nombre.label('proveedor_nombre'),
            Inventario.cantidad_actual,
            Inventario.stock_minimo,
            PrecioProducto.precio
        ).join(
            Categoria, Producto.id_categoria == Categoria.id_categoria
        ).outerjoin(
            Marca, Producto.id_marca == Marca.id_marca
        ).outerjoin(
            Proveedor, Producto.id_proveedor == Proveedor.id_proveedor
        ).outerjoin(
            Inventario, Producto.id_producto == Inventario.id_producto
        ).outerjoin(
            PrecioProducto,
            (Producto.id_producto == PrecioProducto.id_producto) &
            (PrecioProducto.fecha_fin.is_(None))
        ).filter(
            Producto.id_producto == db_product.id_producto
        ).first()

        if not result:
            raise HTTPException(status_code=404, detail="Error al crear el producto")

        response_dict = {
            'id_producto': db_product.id_producto,
            'codigo_producto': db_product.codigo_producto,
            'nombre': db_product.nombre,
            'descripcion': db_product.descripcion,
            'id_categoria': db_product.id_categoria,
            'id_marca': db_product.id_marca,
            'unidad_medida': db_product.unidad_medida,
            'activo': db_product.activo,
            'fecha_creacion': db_product.fecha_creacion,
            'categoria_nombre': result[1] or "",
            'marca_nombre': result[2],
            'proveedor_nombre': result[3],
            'stock_actual': Decimal('0'),
            'stock_minimo': Decimal(str(product.stock_minimo)),
            'precio': Decimal(str(product.precio))
        }

        return response_dict

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
            .outerjoin(Proveedor, Producto.id_proveedor == Proveedor.id_proveedor)
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

        product = result[0]
        product_dict = {
            'id_producto': product.id_producto,
            'codigo_producto': product.codigo_producto,
            'nombre': product.nombre,
            'descripcion': product.descripcion,
            'id_categoria': product.id_categoria,
            'id_marca': product.id_marca,
            'unidad_medida': product.unidad_medida,
            'activo': product.activo,
            'fecha_creacion': product.fecha_creacion,
            'categoria_nombre': result[1] or "",  # Asegurarnos de que nunca sea None
            'marca_nombre': result[2],
            'proveedor_nombre': result[3],
            'stock_actual': Decimal(str(result[4])) if result[4] is not None else Decimal('0'),
            'stock_minimo': Decimal(str(result[5])) if result[5] is not None else Decimal('0'),
            'precio': Decimal(str(result[6])) if result[6] is not None else Decimal('0')
        }

        return product_dict

    def update_product(self, product_id: int, product_data: product_schemas.ProductUpdate) -> dict:
        logger.debug(f"Iniciando actualización del producto {product_id}")
        logger.debug(f"Datos recibidos: {product_data.model_dump()}")

        # Verificar que existe el producto
        product = self.db.query(Producto).filter(Producto.id_producto == product_id).first()
        if not product:
            logger.error(f"Producto {product_id} no encontrado")
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        logger.debug(f"Producto actual en DB: {product.__dict__}")
        
        # Verificar que existe la categoría
        if not self.db.query(Categoria).filter(Categoria.id_categoria == product_data.id_categoria).first():
            logger.error(f"Categoría {product_data.id_categoria} no encontrada")
            raise HTTPException(status_code=400, detail="Categoría no encontrada")
        
        # Verificar que existe la marca si se proporciona
        if product_data.id_marca and not self.db.query(Marca).filter(Marca.id_marca == product_data.id_marca).first():
            raise HTTPException(status_code=400, detail="Marca no encontrada")
        
        # Verificar que existe el proveedor solo si se está actualizando
        if product_data.id_proveedor:
            proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == product_data.id_proveedor).first()
            if not proveedor:
                raise HTTPException(status_code=400, detail="Proveedor no encontrado")

        # Verificar que el código de producto no exista (si se está cambiando)
        if (product_data.codigo_producto != product.codigo_producto and
            self.db.query(Producto).filter(Producto.codigo_producto == product_data.codigo_producto).first()):
            raise HTTPException(status_code=400, detail="El código de producto ya existe")

        # Extraer campos que van en otras tablas, manteniendo id_proveedor
        update_data = product_data.model_dump(exclude={'precio_info', 'inventario_info'})
        logger.debug(f"Datos para actualizar después de model_dump: {update_data}")

        # Si no se proporciona id_proveedor, mantener el existente
        if not update_data.get('id_proveedor'):
            logger.debug(f"No se proporcionó id_proveedor, manteniendo el existente: {product.id_proveedor}")
            update_data['id_proveedor'] = product.id_proveedor
        else:
            logger.debug(f"Nuevo id_proveedor proporcionado: {update_data['id_proveedor']}")

        # Actualizar campos básicos del producto
        logger.debug("Actualizando campos del producto:")
        for key, value in update_data.items():
            try:
                old_value = getattr(product, key)
                logger.debug(f"  {key}: {old_value} -> {value}")
                setattr(product, key, value)
            except AttributeError:
                logger.debug(f"  {key}: no es un atributo directo del producto, valor nuevo: {value}")
                continue

        # Actualizar precio si ha cambiado
        current_price = (
            self.db.query(PrecioProducto.precio)
            .filter(PrecioProducto.id_producto == product_id)
            .filter(PrecioProducto.fecha_fin.is_(None))
            .scalar()
        )
        
        if current_price != product_data.precio:
            # Cerrar precio actual
            self.db.query(PrecioProducto).filter(
                PrecioProducto.id_producto == product_id,
                PrecioProducto.fecha_fin.is_(None)
            ).update({"fecha_fin": datetime.utcnow()})
            
            # Crear nuevo precio
            nuevo_precio = PrecioProducto(
                id_producto=product_id,
                precio=product_data.precio
            )
            self.db.add(nuevo_precio)

        # Actualizar stock_minimo en el inventario existente
        # Buscar el registro de inventario
        inventario = self.db.query(Inventario).filter(
            Inventario.id_producto == product_id
        ).first()

        if inventario:
            # Actualizar stock mínimo usando update
            self.db.query(Inventario).filter(
                Inventario.id_producto == product_id
            ).update({
                'stock_minimo': product_data.stock_minimo
            }, synchronize_session='fetch')
        else:
            # Si no existe inventario, crear uno nuevo con ubicación por defecto
            ubicacion_default = self.db.query(Ubicacion).filter(Ubicacion.activo == True).first()
            if not ubicacion_default:
                raise HTTPException(status_code=400, detail="No hay ubicaciones disponibles para el inventario")
            
            inventario = Inventario(
                id_producto=product_id,
                id_ubicacion=ubicacion_default.id_ubicacion,
                cantidad_actual=0,
                stock_minimo=product_data.stock_minimo
            )
            self.db.add(inventario)
            
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