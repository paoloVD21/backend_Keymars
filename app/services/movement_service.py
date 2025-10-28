from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import (
    Movimiento, MovimientoDetalle, MotivoMovimiento, 
    Inventario, Kardex, Producto, Ubicacion, Usuario, Sucursal, Proveedor
)
from app.schemas import movement_schemas
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import and_
from typing import List

class MovementService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry_movement(self, movement_data: movement_schemas.MovementCreate) -> movement_schemas.MovementDetailedResponse:
        """
        Crea un nuevo movimiento de entrada (ingreso) con sus detalles y actualiza el inventario
        """

        try:
            # Iniciar la transacción
            # Verificar que existe el usuario y está activo
            # Verificar que existe el usuario
            user = self.db.query(Usuario).filter(
                Usuario.id_usuario == movement_data.id_usuario
            ).first()
            
            if not user:
                raise HTTPException(status_code=400, detail="Usuario no encontrado")

            # Verificar que existe el motivo y que cumpla las condiciones
            motivo = self.db.query(MotivoMovimiento).filter(
                MotivoMovimiento.id_motivo == movement_data.id_motivo,
            ).first()
            
            if not motivo:
                raise HTTPException(status_code=400, 
                    detail=f"El motivo con ID {movement_data.id_motivo} no existe")

            # Verificar que existe la sucursal
            # Verificar que existe la sucursal y esté activa
            sucursal = self.db.query(Sucursal).filter(
                Sucursal.id_sucursal == movement_data.id_sucursal
            ).first()
            
            if not sucursal:
                raise HTTPException(status_code=400, detail="Sucursal no encontrada")

            # Verificar que se proporcione un proveedor para el ingreso
            if not movement_data.id_proveedor:
                raise HTTPException(status_code=400, detail="Se requiere un proveedor para los movimientos de ingreso")

            # Verificar que existe el proveedor y está activo
            # Verificar que existe el proveedor y esté activo
            proveedor = self.db.query(Proveedor).filter(
                Proveedor.id_proveedor == movement_data.id_proveedor
            ).first()
            
            if not proveedor:
                raise HTTPException(status_code=400, detail="Proveedor no encontrado")

            # Crear el movimiento
            db_movement = Movimiento(
                tipo_movimiento='INGRESO',
                id_motivo=movement_data.id_motivo,
                id_sucursal=movement_data.id_sucursal,
                id_proveedor=movement_data.id_proveedor,
                numero_documento=None,
                observacion=movement_data.observacion,
                id_usuario=movement_data.id_usuario
            )
            self.db.add(db_movement)
            self.db.flush()

            # Obtener el ID del movimiento
            from sqlalchemy import inspect
            movement_id = inspect(db_movement).identity[0]  # Esto nos da el valor int real

            # Procesar cada detalle del movimiento
            for detail in movement_data.detalles:
                # Verificar producto y ubicación
                self._process_movement_detail(detail, db_movement, movement_data.id_usuario, movement_data)

            # Confirmar todos los cambios
            self.db.commit()
            return self.get_movement_by_id(movement_id)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear el movimiento de ingreso: {str(e)}")

    def create_exit_movement(self, movement_data: movement_schemas.MovementCreate) -> movement_schemas.MovementDetailedResponse:
        """
        Crea un nuevo movimiento de salida (egreso) con sus detalles y actualiza el inventario
        """
        try:
            # Verificar que existe el usuario y está activo
            user = self.db.query(Usuario).filter(
                Usuario.id_usuario == movement_data.id_usuario
            ).first()
            
            if not user:
                raise HTTPException(status_code=400, detail="Usuario no encontrado")

            # Verificar que existe el motivo y que sea de tipo SALIDA
            motivo = self.db.query(MotivoMovimiento).filter(
                and_(
                    MotivoMovimiento.id_motivo == movement_data.id_motivo,
                    MotivoMovimiento.tipo_movimiento == 'SALIDA'
                )
            ).first()
            
            if not motivo:
                raise HTTPException(status_code=400, 
                    detail=f"El motivo con ID {movement_data.id_motivo} no existe o no es un motivo de salida")

            # Verificar que existe la sucursal
            sucursal = self.db.query(Sucursal).filter(
                Sucursal.id_sucursal == movement_data.id_sucursal
            ).first()
            
            if not sucursal:
                raise HTTPException(status_code=400, detail="Sucursal no encontrada")

            # Verificar que NO se proporcione un proveedor para la salida
            if movement_data.id_proveedor is not None:
                raise HTTPException(status_code=400, detail="No se debe especificar proveedor para movimientos de salida")

            # Crear el movimiento
            db_movement = Movimiento(
                tipo_movimiento='EGRESO',
                id_motivo=movement_data.id_motivo,
                id_sucursal=movement_data.id_sucursal,
                id_proveedor=None,
                numero_documento=None,
                observacion=movement_data.observacion,
                id_usuario=movement_data.id_usuario
            )
            self.db.add(db_movement)
            self.db.flush()

            # Obtener el ID del movimiento
            from sqlalchemy import inspect
            movement_id = inspect(db_movement).identity[0]

            # Procesar cada detalle del movimiento
            for detail in movement_data.detalles:
                # Verificar producto, ubicación y stock
                self._process_exit_movement_detail(detail, db_movement, movement_data.id_usuario, movement_data)

            # Confirmar todos los cambios
            self.db.commit()
            return self.get_movement_by_id(movement_id)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear el movimiento de salida: {str(e)}")

    def _process_exit_movement_detail(self, detail, db_movement, usuario_id, movement_data):
        """Procesa un detalle del movimiento de salida"""
        # Verificar que existe el producto
        producto = self.db.query(Producto).filter(
            and_(
                Producto.id_producto == detail.id_producto,
                Producto.activo == True
            )
        ).first()
        if not producto:
            raise HTTPException(
                status_code=400, 
                detail=f"Producto con ID {detail.id_producto} no existe o no está activo"
            )

        # Verificar que existe la ubicación y pertenece a la sucursal
        ubicacion = self.db.query(Ubicacion).filter(
            and_(
                Ubicacion.id_ubicacion == detail.id_ubicacion,
                Ubicacion.id_sucursal == movement_data.id_sucursal,
                Ubicacion.activo == True
            )
        ).first()
        if not ubicacion:
            raise HTTPException(
                status_code=400,
                detail=f"Ubicación {detail.id_ubicacion} no válida para esta sucursal"
            )

        # Buscar el registro en inventario
        inventario = self.db.query(Inventario).filter(
            and_(
                Inventario.id_producto == detail.id_producto,
                Inventario.id_ubicacion == detail.id_ubicacion
            )
        ).first()

        if not inventario:
            raise HTTPException(
                status_code=400,
                detail=f"No existe inventario para el producto {detail.id_producto} en la ubicación {detail.id_ubicacion}"
            )

        # Verificar que hay suficiente stock
        if inventario.cantidad_actual < detail.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para el producto {producto.nombre}. Stock actual: {inventario.cantidad_actual}, Cantidad solicitada: {detail.cantidad}"
            )

        # Registrar el detalle del movimiento
        detalle_movimiento = MovimientoDetalle(
            id_movimiento=db_movement.id_movimiento,
            id_inventario=inventario.id_inventario,
            cantidad=detail.cantidad
        )
        self.db.add(detalle_movimiento)

        # Registrar en kardex
        kardex = Kardex(
            id_inventario=inventario.id_inventario,
            tipo_movimiento='EGRESO',
            id_motivo=movement_data.id_motivo,
            cantidad=detail.cantidad,
            cantidad_anterior=inventario.cantidad_actual,
            cantidad_nueva=inventario.cantidad_actual - detail.cantidad,
            observacion=movement_data.observacion,
            numero_documento=None,
            id_usuario=usuario_id
        )
        self.db.add(kardex)

        # Actualizar cantidad en inventario (restar)
        nueva_cantidad = inventario.cantidad_actual - detail.cantidad
        self.db.query(Inventario).filter(
            Inventario.id_inventario == inventario.id_inventario
        ).update({
            'cantidad_actual': nueva_cantidad,
            'fecha_ultima_actualizacion': datetime.utcnow()
        }, synchronize_session='fetch')

    def _process_movement_detail(self, detail, db_movement, usuario_id, movement_data):
        """Procesa un detalle del movimiento"""
        # Verificar que existe el producto
        producto = self.db.query(Producto).filter(
            and_(
                Producto.id_producto == detail.id_producto,
                Producto.activo == True
            )
        ).first()
        if not producto:
            raise HTTPException(
                status_code=400, 
                detail=f"Producto con ID {detail.id_producto} no existe o no está activo"
            )

        # Verificar que existe la ubicación y pertenece a la sucursal
        ubicacion = self.db.query(Ubicacion).filter(
            and_(
                Ubicacion.id_ubicacion == detail.id_ubicacion,
                Ubicacion.id_sucursal == movement_data.id_sucursal,
                Ubicacion.activo == True
            )
        ).first()
        if not ubicacion:
            raise HTTPException(
                status_code=400,
                detail=f"Ubicación {detail.id_ubicacion} no válida para esta sucursal"
            )

        # Buscar o crear registro en inventario
        inventario = self.db.query(Inventario).filter(
            and_(
                Inventario.id_producto == detail.id_producto,
                Inventario.id_ubicacion == detail.id_ubicacion
            )
        ).first()

        if not inventario:
            # Crear nuevo registro de inventario
            inventario = Inventario(
                id_producto=detail.id_producto,
                id_ubicacion=detail.id_ubicacion,
                cantidad_actual=Decimal('0'),
                stock_minimo=Decimal('0')
            )
            self.db.add(inventario)
            self.db.flush()

        # Registrar el detalle del movimiento
        detalle_movimiento = MovimientoDetalle(
            id_movimiento=db_movement.id_movimiento,
            id_inventario=inventario.id_inventario,
            cantidad=detail.cantidad
        )
        self.db.add(detalle_movimiento)

        # Registrar en kardex
        kardex = Kardex(
            id_inventario=inventario.id_inventario,
            tipo_movimiento='INGRESO',
            id_motivo=movement_data.id_motivo,
            cantidad=detail.cantidad,
            cantidad_anterior=inventario.cantidad_actual,
            cantidad_nueva=inventario.cantidad_actual + detail.cantidad,
            observacion=movement_data.observacion,
            numero_documento=None,
            id_usuario=usuario_id
        )
        self.db.add(kardex)

        # Actualizar cantidad en inventario
        nueva_cantidad = inventario.cantidad_actual + detail.cantidad
        self.db.query(Inventario).filter(
            Inventario.id_inventario == inventario.id_inventario
        ).update({
            'cantidad_actual': nueva_cantidad,
            'fecha_ultima_actualizacion': datetime.utcnow()
        }, synchronize_session='fetch')

    def search_products_for_movement(self, id_sucursal: int, buscar: str) -> List[movement_schemas.ProductoSearchResponse]:
        """
        Busca productos por nombre o código y obtiene su stock en la sucursal especificada
        """
        import logging
        from sqlalchemy import or_, func
        logger = logging.getLogger(__name__)

        logger.info(f"Iniciando búsqueda de productos en sucursal ID: {id_sucursal}")
        logger.info(f"Término de búsqueda: '{buscar}'")

        try:
            # Verificar que la sucursal existe y está activa
            sucursal = self.db.query(Sucursal).filter(
                and_(
                    Sucursal.id_sucursal == id_sucursal,
                    Sucursal.activo == True
                )
            ).first()
            
            if not sucursal:
                logger.error(f"Sucursal ID {id_sucursal} no encontrada o inactiva")
                raise HTTPException(status_code=404, detail="Sucursal no encontrada o inactiva")
            
            logger.info(f"Búsqueda en sucursal: {sucursal.nombre}")

            # Buscar productos que coincidan con el término de búsqueda
            logger.debug("Ejecutando consulta de búsqueda de productos...")
            productos = (
                self.db.query(
                    Producto.id_producto,
                    Producto.nombre,
                    Producto.codigo_producto,
                    Producto.precio,
                    Inventario.cantidad_actual,
                    Ubicacion.id_ubicacion,
                    Ubicacion.nombre.label('nombre_ubicacion')
                )
                .join(
                    Inventario,
                    Producto.id_producto == Inventario.id_producto
                )
                .join(
                    Ubicacion,
                    and_(
                        Inventario.id_ubicacion == Ubicacion.id_ubicacion,
                        Ubicacion.id_sucursal == id_sucursal,
                        Ubicacion.activo == True
                    )
                )
                .filter(
                    and_(
                        Producto.activo == True,
                        or_(
                            func.lower(Producto.nombre).contains(func.lower(buscar)),
                            func.lower(Producto.codigo_producto).contains(func.lower(buscar))
                        )
                    )
                )
                .all()
            )

            total_productos = len(productos)
            logger.info(f"Se encontraron {total_productos} resultados que coinciden con la búsqueda")
            
            if total_productos == 0:
                logger.info(f"No se encontraron productos que coincidan con el término '{buscar}'")
                return []

            # Agrupar los resultados por producto
            logger.debug("Agrupando resultados por producto...")
            productos_agrupados = {}
            for producto in productos:
                id_producto = producto[0]
                if id_producto not in productos_agrupados:
                    logger.debug(f"Procesando producto: {producto[1]} (ID: {id_producto}, Código: {producto[2]})")
                    productos_agrupados[id_producto] = {
                        'id_producto': id_producto,
                        'nombre_producto': producto[1],
                        'codigo_producto': producto[2],
                        'precio': float(producto[3]),
                        'stock_ubicaciones': []
                    }

                stock_actual = float(producto[4] if producto[4] is not None else 0)
                logger.debug(f"Stock en ubicación '{producto[6]}': {stock_actual}")
                productos_agrupados[id_producto]['stock_ubicaciones'].append({
                    'id_ubicacion': producto[5],
                    'nombre_ubicacion': producto[6],
                    'stock_actual': stock_actual
                })

            # Convertir el diccionario a una lista de respuestas
            logger.debug("Generando respuesta final...")
            resultados = [
                movement_schemas.ProductoSearchResponse(**producto_info)
                for producto_info in productos_agrupados.values()
            ]

            num_productos_unicos = len(resultados)
            logger.info(f"Procesamiento completado. Productos únicos encontrados: {num_productos_unicos}")
            logger.info("Desglose de productos encontrados:")
            for resultado in resultados:
                total_stock = sum(ub.stock_actual for ub in resultado.stock_ubicaciones)
                logger.info(f"- {resultado.nombre_producto} (Código: {resultado.codigo_producto})")
                logger.info(f"  Precio: {resultado.precio}, Stock total: {total_stock}")
                logger.info(f"  Ubicaciones encontradas: {len(resultado.stock_ubicaciones)}")
                for ubicacion in resultado.stock_ubicaciones:
                    logger.info(f"    * {ubicacion.nombre_ubicacion}: {ubicacion.stock_actual} unidades")

            return resultados

        except Exception as e:
            logger.error(f"Error durante la búsqueda de productos: {str(e)}")
            raise

    def get_movements_by_date(self, date: datetime) -> List[movement_schemas.MovementListResponse]:
        """
        Obtiene un resumen de los movimientos realizados en una fecha específica
        """
        from sqlalchemy import func

        movements = (
            self.db.query(
                Movimiento,
                Usuario.nombre.concat(' ').concat(Usuario.apellido).label('nombre_usuario'),
                MotivoMovimiento.nombre.label('motivo_nombre'),
                Sucursal.nombre.label('sucursal_nombre'),
                Proveedor.nombre.label('proveedor_nombre')
            )
            .join(Usuario, Movimiento.id_usuario == Usuario.id_usuario)
            .join(MotivoMovimiento, Movimiento.id_motivo == MotivoMovimiento.id_motivo)
            .join(Sucursal, Movimiento.id_sucursal == Sucursal.id_sucursal)
            .outerjoin(Proveedor, Movimiento.id_proveedor == Proveedor.id_proveedor)
            .filter(func.date(Movimiento.fecha_movimiento) == date.date())
            .order_by(Movimiento.fecha_movimiento.desc())
            .all()
        )

        result = []
        for movement in movements:
            # Obtener los detalles para cada movimiento
            detalles = (
                self.db.query(
                    MovimientoDetalle,
                    Producto.nombre.label('nombre_producto'),
                    Producto.codigo_producto,
                    Ubicacion.nombre.label('ubicacion_nombre')
                )
                .join(Inventario, MovimientoDetalle.id_inventario == Inventario.id_inventario)
                .join(Producto, Inventario.id_producto == Producto.id_producto)
                .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
                .filter(MovimientoDetalle.id_movimiento == movement[0].id_movimiento)
                .all()
            )

            # Calcular la cantidad total
            cantidad_total = sum(detalle[0].cantidad for detalle in detalles)

            # Construir la respuesta resumida para cada movimiento
            result.append(movement_schemas.MovementListResponse(
                id_movimiento=movement[0].id_movimiento,
                motivo_nombre=movement[2],
                proveedor_nombre=movement[4],
                nombre_usuario=movement[1],
                sucursal_nombre=movement[3],
                cantidad_total=cantidad_total
            ))

        return result

    def get_movement_by_id(self, movement_id: int) -> movement_schemas.MovementDetailedResponse:
        """
        Obtiene un movimiento por su ID con todos sus detalles
        """
        movement = (
            self.db.query(
                Movimiento,
                Usuario.nombre.concat(' ').concat(Usuario.apellido).label('nombre_usuario'),
                MotivoMovimiento.nombre.label('motivo_nombre'),
                Sucursal.nombre.label('sucursal_nombre'),
                Proveedor.nombre.label('proveedor_nombre')
            )
            .join(Usuario, Movimiento.id_usuario == Usuario.id_usuario)
            .join(MotivoMovimiento, Movimiento.id_motivo == MotivoMovimiento.id_motivo)
            .join(Sucursal, Movimiento.id_sucursal == Sucursal.id_sucursal)
            .outerjoin(Proveedor, Movimiento.id_proveedor == Proveedor.id_proveedor)
            .filter(Movimiento.id_movimiento == movement_id)
            .first()
        )

        if not movement:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")

        # Obtener los detalles
        detalles = (
            self.db.query(
                MovimientoDetalle,
                Producto.nombre.label('nombre_producto'),
                Producto.codigo_producto,
                Ubicacion.nombre.label('ubicacion_nombre')
            )
            .join(Inventario, MovimientoDetalle.id_inventario == Inventario.id_inventario)
            .join(Producto, Inventario.id_producto == Producto.id_producto)
            .join(Ubicacion, Inventario.id_ubicacion == Ubicacion.id_ubicacion)
            .filter(MovimientoDetalle.id_movimiento == movement_id)
            .all()
        )

        # Crear la lista de detalles primero
        detalles_lista = []
        for detalle in detalles:
            # Obtener el precio del producto
            producto = self.db.query(Producto).filter(
                Producto.id_producto == detalle[0].inventario.id_producto
            ).first()
            
            precio_unitario = Decimal(str(producto.precio)) if producto else Decimal('0')
            cantidad = int(detalle[0].cantidad)  # Convertimos a int ya que la cantidad siempre será entera
            precio_total = precio_unitario * Decimal(str(cantidad))
            
            detalles_lista.append(
                movement_schemas.MovementDetailResponse(
                    id_movimiento_detalle=detalle[0].id_movimiento_detalle,
                    id_producto=detalle[0].inventario.id_producto,
                    id_ubicacion=detalle[0].inventario.id_ubicacion,
                    nombre_producto=detalle[1],
                    codigo_producto=detalle[2],
                    ubicacion_nombre=detalle[3],
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    precio_total=precio_total
                )
            )

        # Construir la respuesta
        return movement_schemas.MovementDetailedResponse(
            id_movimiento=movement[0].id_movimiento,
            motivo_nombre=movement[2],
            proveedor_nombre=movement[4],
            nombre_usuario=movement[1],
            sucursal_nombre=movement[3],
            detalles=detalles_lista,
            cantidad_total=sum(d.cantidad for d in detalles_lista)
        )