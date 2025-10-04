from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.services.services import ProductoService
from app.schemas import schemas

router = APIRouter()

@router.get("/productos/", response_model=List[schemas.Producto])
def get_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    productos = ProductoService.get_productos(db, skip=skip, limit=limit)
    return productos

@router.get("/productos/{producto_id}", response_model=schemas.Producto)
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = ProductoService.get_producto(db, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/productos/", response_model=schemas.Producto)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    return ProductoService.create_producto(db=db, producto=producto)

@router.put("/productos/{producto_id}", response_model=schemas.Producto)
def update_producto(producto_id: int, producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    updated_producto = ProductoService.update_producto(db, producto_id, producto)
    if updated_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return updated_producto

@router.delete("/productos/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    success = ProductoService.delete_producto(db, producto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado exitosamente"}