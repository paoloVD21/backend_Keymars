from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import (
    Movimiento, MovimientoDetalle, MotivoMovimiento, 
    Inventario, Kardex, Producto, Ubicacion, Usuario, Sucursal, Proveedor
)
from app.schemas import movement_schemas
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_

class MovementService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry_movement(self, movement_data: movement_schemas.MovementCreate) -> movement_schemas.MovementResponse:
        """
        Crea un nuevo movimiento de entrada (ingreso) con sus detalles y actualiza el inventario
        """
        print("\n--------- VALIDACIÓN DE DATOS EN SERVICIO ---------")
        
        # Usar el id_usuario del objeto movement_data
        print(f"ID Usuario: {movement_data.id_usuario}")
        print(f"ID Motivo: {movement_data.id_motivo}")
        print(f"ID Sucursal: {movement_data.id_sucursal}")
        print(f"ID Proveedor: {movement_data.id_proveedor}")
        print("Detalles:")
        for detalle in movement_data.detalles:
            print(f"  * Producto: {detalle.id_producto}, Ubicación: {detalle.id_ubicacion}, Cantidad: {detalle.cantidad}")
        
        try:
            # Iniciar la transacción
            # Verificar que existe el usuario y está activo
            # Verificar que existe el usuario
            user = self.db.query(Usuario).filter(
                Usuario.id_usuario == movement_data.id_usuario
            ).first()
            
            if not user:
                print(f"Error: Usuario {movement_data.id_usuario} no encontrado")
                raise HTTPException(status_code=400, detail="Usuario no encontrado")
            
            print(f"Usuario validado: {user.nombre} {user.apellido}")

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
            print(f"Error inesperado: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al crear el movimiento de ingreso: {str(e)}")

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

    def get_movement_by_id(self, movement_id: int) -> movement_schemas.MovementResponse:
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

        # Construir la respuesta
        return movement_schemas.MovementResponse(
            id_movimiento=movement[0].id_movimiento,
            tipo_movimiento=movement[0].tipo_movimiento,
            numero_documento=movement[0].numero_documento,
            observacion=movement[0].observacion,
            fecha_movimiento=movement[0].fecha_movimiento,
            nombre_usuario=movement[1],
            motivo_nombre=movement[2],
            sucursal_nombre=movement[3],
            proveedor_nombre=movement[4],
            detalles=[
                movement_schemas.MovementDetailResponse(
                    id_movimiento_detalle=detalle[0].id_movimiento_detalle,
                    id_producto=detalle[0].inventario.id_producto,  # Acceder a través de la relación
                    id_ubicacion=detalle[0].inventario.id_ubicacion,  # Acceder a través de la relación
                    nombre_producto=detalle[1],
                    codigo_producto=detalle[2],
                    ubicacion_nombre=detalle[3],
                    cantidad=detalle[0].cantidad
                )
                for detalle in detalles
            ]
        )