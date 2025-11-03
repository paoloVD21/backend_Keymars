from fpdf import FPDF
from datetime import datetime

class PDFReportGenerator:
    @staticmethod
    def generate_inventory_summary(data, periodo: str, sucursal_id: int):
        pdf = FPDF()
        pdf.add_page()
        
        # Configuración de fuente
        pdf.set_font('Arial', 'B', 16)
        
        # Título
        pdf.cell(190, 10, 'Reporte: Resumen de Inventario', 0, 1, 'C')
        
        # Información del reporte
        pdf.set_font('Arial', '', 12)
        pdf.cell(190, 10, f'Período: {periodo}', 0, 1, 'L')
        pdf.cell(190, 10, f'Sucursal: {sucursal_id}', 0, 1, 'L')
        pdf.cell(190, 10, f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'L')
        
        # Encabezados de tabla
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(30, 10, 'Código', 1)
        pdf.cell(50, 10, 'Producto', 1)
        pdf.cell(40, 10, 'Ubicación', 1)
        pdf.cell(25, 10, 'Stock', 1)
        pdf.cell(25, 10, 'Mínimo', 1)
        pdf.cell(20, 10, 'Valor', 1)
        pdf.ln()
        
        # Contenido de la tabla
        pdf.set_font('Arial', '', 12)
        for item in data:
            pdf.cell(30, 10, str(item.get('codigo_producto')), 1)
            pdf.cell(50, 10, str(item.get('nombre_producto')), 1)
            pdf.cell(40, 10, str(item.get('ubicacion')), 1)
            pdf.cell(25, 10, str(item.get('stock_actual')), 1)
            pdf.cell(25, 10, str(item.get('stock_minimo')), 1)
            pdf.cell(20, 10, str(item.get('valor_total')), 1)
            pdf.ln()
            
        return pdf

    @staticmethod
    def generate_low_stock_report(data, periodo: str, sucursal_id: int):
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(190, 10, 'Reporte: Productos con Stock Bajo', 0, 1, 'C')
        
        # Información del reporte
        pdf.set_font('Arial', '', 12)
        pdf.cell(190, 10, f'Período: {periodo}', 0, 1, 'L')
        pdf.cell(190, 10, f'Sucursal: {sucursal_id}', 0, 1, 'L')
        pdf.cell(190, 10, f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'L')
        
        # Encabezados de tabla
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(30, 10, 'Código', 1)
        pdf.cell(50, 10, 'Producto', 1)
        pdf.cell(40, 10, 'Ubicación', 1)
        pdf.cell(25, 10, 'Stock', 1)
        pdf.cell(25, 10, 'Mínimo', 1)
        pdf.cell(20, 10, 'Dif.', 1)
        pdf.ln()
        
        # Contenido de la tabla
        pdf.set_font('Arial', '', 12)
        for item in data:
            pdf.cell(30, 10, str(item.get('codigo_producto')), 1)
            pdf.cell(50, 10, str(item.get('nombre_producto')), 1)
            pdf.cell(40, 10, str(item.get('ubicacion')), 1)
            pdf.cell(25, 10, str(item.get('stock_actual')), 1)
            pdf.cell(25, 10, str(item.get('stock_minimo')), 1)
            pdf.cell(20, 10, str(item.get('diferencia')), 1)
            pdf.ln()
            
        return pdf

    @staticmethod
    def generate_movement_summary(data, periodo: str, sucursal_id: int):
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(190, 10, 'Reporte: Mayores Movimientos', 0, 1, 'C')
        
        # Información del reporte
        pdf.set_font('Arial', '', 12)
        pdf.cell(190, 10, f'Período: {periodo}', 0, 1, 'L')
        pdf.cell(190, 10, f'Sucursal: {sucursal_id}', 0, 1, 'L')
        pdf.cell(190, 10, f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'L')
        
        # Encabezados de tabla
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(30, 10, 'Código', 1)
        pdf.cell(50, 10, 'Producto', 1)
        pdf.cell(35, 10, 'Entradas', 1)
        pdf.cell(35, 10, 'Salidas', 1)
        pdf.cell(40, 10, 'Total Mov.', 1)
        pdf.ln()
        
        # Contenido de la tabla
        pdf.set_font('Arial', '', 12)
        for item in data:
            pdf.cell(30, 10, str(item.get('codigo_producto')), 1)
            pdf.cell(50, 10, str(item.get('nombre_producto')), 1)
            pdf.cell(35, 10, str(item.get('total_entradas')), 1)
            pdf.cell(35, 10, str(item.get('total_salidas')), 1)
            pdf.cell(40, 10, str(item.get('movimientos_totales')), 1)
            pdf.ln()
            
        return pdf