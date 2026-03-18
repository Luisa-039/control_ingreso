from pydantic import BaseModel, Field
from typing import Optional

class CategorieBase(BaseModel):
    nombre_categoria: str = Field(min_length=3, max_length=30)
    descripcion: str = Field(min_length=3, max_length=100)
    estado: bool

class CategorieCreate(CategorieBase):
    pass

class CategorieUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=30)
    descripcion: Optional[str] = Field(default=None, min_length=3, max_length=100)

class CategorieEstado(BaseModel):
    estado: Optional[bool] = None

class CategorieOut(CategorieBase):
    id_categoria: int
