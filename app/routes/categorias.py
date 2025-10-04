from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.services.services import CategoriaService
from app.schemas import schemas

router = APIRouter()

@router.get("/categorias/", response_model=List[schemas.Categoria])
def get_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categorias = CategoriaService.get_categorias(db, skip=skip, limit=limit)
    return categorias

@router.get("/categorias/{categoria_id}", response_model=schemas.Categoria)
def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = CategoriaService.get_categoria(db, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router.post("/categorias/", response_model=schemas.Categoria)
def create_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    return CategoriaService.create_categoria(db=db, categoria=categoria)