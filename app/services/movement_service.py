from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import (
    Movimiento, MovimientoDetalle, MotivoMovimiento, 
    Inventario, Kardex, Producto, Ubicacion, Usuario, Sucursal
)
from app.schemas import movement_schemas
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_

class MovementService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry_movement(self, movement_data: movement_schemas.MovementCreate, user_id: int) -> movement_schemas.MovementResponse:
        """
        Crea un nuevo movimiento de entrada (ingreso) con sus detalles y actualiza el inventario
        """
        # Verificar que existe el motivo y es de tipo INGRESO
        motivo = self.db.query(MotivoMovimiento).filter(
            and_(
                MotivoMovimiento.id_motivo == movement_data.id_motivo,
                MotivoMovimiento.tipo_movimiento == 'INGRESO',
                MotivoMovimiento.activo == True
            )
        ).first()
        if not motivo:
            raise HTTPException(status_code=400, detail="Motivo de ingreso no válido")

        # Verificar que existe la sucursal
        sucursal = self.db.query(Sucursal).filter(
            and_(
                Sucursal.id_sucursal == movement_data.id_sucursal,
                Sucursal.activo == True
            )
        ).first()
        if not sucursal:
            raise HTTPException(status_code=400, detail="Sucursal no válida")

        # Crear el movimiento
        db_movement = Movimiento(
            tipo_movimiento='INGRESO',
            id_motivo=movement_data.id_motivo,
            id_sucursal=movement_data.id_sucursal,
            numero_documento=None,  # Ya no se recibe del frontend
            observacion=movement_data.observacion,
            id_usuario=user_id
        )
        # Crear el movimiento y obtener su ID usando inspect
        self.db.add(db_movement)
        self.db.flush()
        from sqlalchemy import inspect
        movement_id = inspect(db_movement).identity[0]  # Obtener el ID primario usando inspect

        # Procesar cada detalle
        for detail in movement_data.detalles:
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
                numero_documento=None,  # Ya no se recibe del frontend
                id_usuario=user_id
            )
            self.db.add(kardex)

            # Actualizar cantidad en inventario usando update()
            nueva_cantidad = inventario.cantidad_actual + detail.cantidad
            self.db.query(Inventario).filter(
                Inventario.id_inventario == inventario.id_inventario
            ).update({
                'cantidad_actual': nueva_cantidad,
                'fecha_ultima_actualizacion': datetime.utcnow()
            }, synchronize_session='fetch')

        try:
            self.db.commit()
            # Usar el ID guardado después del flush
            return self.get_movement_by_id(movement_id)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear el movimiento de ingreso")

    def get_movement_by_id(self, movement_id: int) -> movement_schemas.MovementResponse:
        """
        Obtiene un movimiento por su ID con todos sus detalles
        """
        movement = (
            self.db.query(
                Movimiento,
                Usuario.nombre.concat(' ').concat(Usuario.apellido).label('nombre_usuario'),
                MotivoMovimiento.nombre.label('motivo_nombre'),
                Sucursal.nombre.label('sucursal_nombre')
            )
            .join(Usuario, Movimiento.id_usuario == Usuario.id_usuario)
            .join(MotivoMovimiento, Movimiento.id_motivo == MotivoMovimiento.id_motivo)
            .join(Sucursal, Movimiento.id_sucursal == Sucursal.id_sucursal)
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