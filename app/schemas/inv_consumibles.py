from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

    
class Inv_consumibleBase(BaseModel):
    sede_id: int
    categoria_id: int
    placa: Optional[str] = None
    marca: str
    modelo: str
    ubicacion: Optional[str] = None
    cantidad:int
    fecha_registro: datetime
    porcentaje_toner: Optional[int] = None

class Inv_consumibleCreate(Inv_consumibleBase):
    pass

class Inv_consumibleUpdate(BaseModel):
    sede_id: Optional[int] = Field(default=None)
    categoria_id: Optional[int] = Field(default=None)
    placa: Optional[str] = Field(default=None,min_length=3, max_length=70)
    marca: Optional[str] = Field(default=None,min_length=3, max_length=50)
    modelo: Optional[str] = Field(default=None,min_length=3, max_length=50)
    ubicacion: Optional[str] = Field(default=None, min_length=3, max_length=70)
    cantidad: Optional[int] = Field(default=None)
    porcentaje_toner: Optional[int] = Field(default=None)

class Inv_consumibleEstado(BaseModel):
    estado: bool

class Inv_consumibleOut(Inv_consumibleBase):
    id_consumible: int
    nombre_sede: str
    nombre_categoria: str
    estado: bool
    
class PaginatedInv_consumibles(BaseModel):
    page: int
    page_size: int
    total_consumibles: int
    total_pages: int
    consumibles: List[Inv_consumibleOut]
