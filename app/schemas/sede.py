from pydantic import BaseModel, Field
from typing import Optional, List

class SedeBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    direccion: str = Field(min_length=3, max_length=100)
    codigo_sede: str = Field(min_length=3, max_length=15)
    centro_id: int
    estado: bool

class SedeCreate(SedeBase):
    pass

class SedeUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=100)
    direccion: Optional[str] = Field(default=None, min_length=3, max_length=100)

class SedeEstado(BaseModel):
    estado: Optional[bool] = None

class SedeOut(SedeBase):
    id_sede: int
    centro_id: int
    nombre_centro: str
    
class PaginatedSede(BaseModel):
    page: int
    page_size: int
    total_sedes: int
    total_pages: int
    sedes: List[SedeOut]
