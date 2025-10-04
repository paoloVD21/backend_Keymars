from sqlalchemy.orm import Session
from app.models.models import Producto, Categoria
from app.schemas import schemas
from typing import List, Optional
from datetime import datetime

class ProductoService:
    @staticmethod
    def get_productos(db: Session, skip: int = 0, limit: int = 100) -> List[Producto]:
        return db.query(Producto).offset(skip).limit(limit).all()

    @staticmethod
    def get_producto(db: Session, producto_id: int) -> Optional[Producto]:
        return db.query(Producto).filter(Producto.id == producto_id).first()

    @staticmethod
    def create_producto(db: Session, producto: schemas.ProductoCreate) -> Producto:
        db_producto = Producto(**producto.model_dump())
        db.add(db_producto)
        db.commit()
        db.refresh(db_producto)
        return db_producto

    @staticmethod
    def update_producto(db: Session, producto_id: int, producto: schemas.ProductoCreate) -> Optional[Producto]:
        db_producto = ProductoService.get_producto(db, producto_id)
        if db_producto:
            for key, value in producto.model_dump().items():
                setattr(db_producto, key, value)
            db_producto.fecha_actualizacion = datetime.utcnow()
            db.commit()
            db.refresh(db_producto)
        return db_producto

    @staticmethod
    def delete_producto(db: Session, producto_id: int) -> bool:
        db_producto = ProductoService.get_producto(db, producto_id)
        if db_producto:
            db.delete(db_producto)
            db.commit()
            return True
        return False

class CategoriaService:
    @staticmethod
    def get_categorias(db: Session, skip: int = 0, limit: int = 100) -> List[Categoria]:
        return db.query(Categoria).offset(skip).limit(limit).all()

    @staticmethod
    def get_categoria(db: Session, categoria_id: int) -> Optional[Categoria]:
        return db.query(Categoria).filter(Categoria.id == categoria_id).first()

    @staticmethod
    def create_categoria(db: Session, categoria: schemas.CategoriaCreate) -> Categoria:
        db_categoria = Categoria(**categoria.model_dump())
        db.add(db_categoria)
        db.commit()
        db.refresh(db_categoria)
        return db_categoria