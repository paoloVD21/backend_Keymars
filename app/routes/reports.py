from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.report_schemas import ReportType, Period
from app.services.reports.report_service import ReportService
from app.services.reports.excel_generator import ExcelReportGenerator
from app.services.reports.pdf_generator import PDFReportGenerator
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import os

class ReportRequest(BaseModel):
    tipo_reporte: ReportType
    periodo: Period
    id_sucursal: int

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"]
)

@router.post("/excel")
async def generate_excel_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Genera un reporte en formato Excel
    
    - **tipo_reporte**: Tipo de reporte (resumen_inventario, stock_bajo, mayores_movimientos)
    - **periodo**: Período del reporte (ultimo_mes, ultimo_trimestre, ultimo_anio)
    - **id_sucursal**: ID de la sucursal
    """
    temp_file = None
    try:
        report_service = ReportService(db)
        
        # Obtener los datos según el tipo de reporte
        if report_request.tipo_reporte == ReportType.INVENTORY_SUMMARY:
            data = report_service.get_inventory_summary(report_request.periodo, report_request.id_sucursal)
            workbook = ExcelReportGenerator.generate_inventory_summary(
                data, report_request.periodo, report_request.id_sucursal
            )
        elif report_request.tipo_reporte == ReportType.LOW_STOCK:
            data = report_service.get_low_stock_report(report_request.periodo, report_request.id_sucursal)
            workbook = ExcelReportGenerator.generate_low_stock_report(
                data, report_request.periodo, report_request.id_sucursal
            )
        elif report_request.tipo_reporte == ReportType.MOVEMENT_SUMMARY:
            data = report_service.get_movement_summary(report_request.periodo, report_request.id_sucursal)
            workbook = ExcelReportGenerator.generate_movement_summary(
                data, report_request.periodo, report_request.id_sucursal
            )
        else:
            raise HTTPException(status_code=400, detail="Tipo de reporte no válido")

        # Crear archivo temporal y guardar
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        workbook.save(temp_file.name)
        
        # Generar nombre de archivo
        filename = f"reporte_{report_request.tipo_reporte}_{report_request.periodo}_{report_request.id_sucursal}.xlsx"
        
        # Devolver el archivo
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            background=None
        )

    except Exception as e:
        if temp_file is not None and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf")
async def generate_pdf_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Genera un reporte en formato PDF
    
    - **tipo_reporte**: Tipo de reporte (resumen_inventario, stock_bajo, mayores_movimientos)
    - **periodo**: Período del reporte (ultimo_mes, ultimo_trimestre, ultimo_anio)
    - **id_sucursal**: ID de la sucursal
    """
    temp_file = None
    try:
        report_service = ReportService(db)
        
        # Obtener los datos según el tipo de reporte
        if report_request.tipo_reporte == ReportType.INVENTORY_SUMMARY:
            data = report_service.get_inventory_summary(report_request.periodo, report_request.id_sucursal)
            pdf = PDFReportGenerator.generate_inventory_summary(
                data, report_request.periodo, report_request.id_sucursal
            )
        elif report_request.tipo_reporte == ReportType.LOW_STOCK:
            data = report_service.get_low_stock_report(report_request.periodo, report_request.id_sucursal)
            pdf = PDFReportGenerator.generate_low_stock_report(
                data, report_request.periodo, report_request.id_sucursal
            )
        elif report_request.tipo_reporte == ReportType.MOVEMENT_SUMMARY:
            data = report_service.get_movement_summary(report_request.periodo, report_request.id_sucursal)
            pdf = PDFReportGenerator.generate_movement_summary(
                data, report_request.periodo, report_request.id_sucursal
            )
        else:
            raise HTTPException(status_code=400, detail="Tipo de reporte no válido")

        # Crear archivo temporal y guardar
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        pdf.output(temp_file.name)
        
        # Generar nombre de archivo
        filename = f"reporte_{report_request.tipo_reporte}_{report_request.periodo}_{report_request.id_sucursal}.pdf"
        
        # Devolver el archivo
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type="application/pdf",
            background=None
        )

    except Exception as e:
        if temp_file is not None and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    temp_file = None
    try:
        report_service = ReportService(db)
        
        # Obtener los datos según el tipo de reporte
        if report_request.tipo_reporte == ReportType.INVENTORY_SUMMARY:
            data = report_service.get_inventory_summary(report_request.periodo, report_request.id_sucursal)
        elif report_request.tipo_reporte == ReportType.LOW_STOCK:
            data = report_service.get_low_stock_report(report_request.periodo, report_request.id_sucursal)
        elif report_request.tipo_reporte == ReportType.MOVEMENT_SUMMARY:
            data = report_service.get_movement_summary(report_request.periodo, report_request.id_sucursal)
        else:
            raise HTTPException(status_code=400, detail="Tipo de reporte no válido")

        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        
        # Generar el reporte en el formato solicitado
        if report_request.formato == ReportFormat.EXCEL:
            if report_request.tipo_reporte == ReportType.INVENTORY_SUMMARY:
                workbook = ExcelReportGenerator.generate_inventory_summary(
                    data, report_request.periodo, report_request.id_sucursal
                )
            elif report_request.tipo_reporte == ReportType.LOW_STOCK:
                workbook = ExcelReportGenerator.generate_low_stock_report(
                    data, report_request.periodo, report_request.id_sucursal
                )
            else:  # MOVEMENT_SUMMARY
                workbook = ExcelReportGenerator.generate_movement_summary(
                    data, report_request.periodo, report_request.id_sucursal
                )
                
            workbook.save(temp_file.name)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_extension = "xlsx"
            
        else:  # PDF
            if report_request.tipo_reporte == ReportType.INVENTORY_SUMMARY:
                pdf = PDFReportGenerator.generate_inventory_summary(
                    data, report_request.periodo, report_request.id_sucursal
                )
            elif report_request.tipo_reporte == ReportType.LOW_STOCK:
                pdf = PDFReportGenerator.generate_low_stock_report(
                    data, report_request.periodo, report_request.id_sucursal
                )
            else:  # MOVEMENT_SUMMARY
                pdf = PDFReportGenerator.generate_movement_summary(
                    data, report_request.periodo, report_request.id_sucursal
                )
                
            pdf.output(temp_file.name)
            media_type = "application/pdf"
            file_extension = "pdf"

        # Generar nombre de archivo
        filename = f"reporte_{report_request.tipo_reporte}_{report_request.periodo}_{report_request.id_sucursal}.{file_extension}"
        
        # Devolver el archivo
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type=media_type,
            background=None  # Para que el archivo se elimine después de enviarlo
        )

    except Exception as e:
        # Si ocurre un error, eliminar el archivo temporal si existe
        if temp_file is not None and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass  # Ignorar errores al eliminar el archivo
        raise HTTPException(status_code=500, detail=str(e))