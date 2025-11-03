from pydantic import BaseModel
from typing import List

class TendenciaData(BaseModel):
    valor: str
    esPositivo: bool

class TendenciasStats(BaseModel):
    productos: TendenciaData
    stock: TendenciaData
    proveedores: TendenciaData

class DashboardStats(BaseModel):
    totalProductos: int
    stockDisponible: float
    proveedoresActivos: int
    tendencias: TendenciasStats

class MovimientosData(BaseModel):
    labels: List[str]  # meses
    entradas: List[float]
    salidas: List[float]

class DistribucionData(BaseModel):
    labels: List[str]  # categorías
    data: List[float]  # cantidades