from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import MotivoMovimiento
from app.schemas import movement_reason_schemas
from typing import List

class MovementReasonController:
    @staticmethod
    async def get_movement_reasons_by_type(
        tipo_movimiento: str,
        db: Session
    ) -> List[movement_reason_schemas.MovementReasonResponse]:
        """
        Obtiene todos los motivos de movimiento activos por tipo (ENTRADA o SALIDA)
        """
        try:
            motivos = (
                db.query(
                    MotivoMovimiento.id_motivo.label('id_motivo'),
                    MotivoMovimiento.nombre.label('nombre'),
                    MotivoMovimiento.tipo_movimiento.label('tipo_movimiento'),
                    MotivoMovimiento.activo.label('activo')
                )
                .filter(
                    and_(
                        MotivoMovimiento.tipo_movimiento == tipo_movimiento,
                        MotivoMovimiento.activo == True
                    )
                )
                .all()
            )

            if not motivos:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No se encontraron motivos de {tipo_movimiento.lower()}"
                )

            # Convertir los resultados a esquemas
            return [
                movement_reason_schemas.MovementReasonResponse(
                    id_motivo=motivo.id_motivo,
                    nombre=motivo.nombre,
                    tipo_movimiento=motivo.tipo_movimiento,
                    activo=motivo.activo
                )
                for motivo in motivos
            ]
        except Exception as e:
            print(f"Error al obtener motivos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error al obtener los motivos de movimiento"
            )