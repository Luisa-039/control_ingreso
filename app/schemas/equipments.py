from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class TipoEquipo(str, Enum):
    computador = "Computador"
    herramienta = "Herramienta"
    otro = "Otro"
    
class EquipoBase(BaseModel):
    serial: Optional[str] = None
    descripcion: str
    tipo_equipo: Optional[TipoEquipo] = None
    foto_path: Optional[str]
    marca_modelo: str
    persona_id: int
    fecha_registro: datetime
    estado: bool
    codigo_barras_inv: Optional[str] = None

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    tipo_equipo: Optional[TipoEquipo] = None
    foto_path: Optional[str] = Field(default=None, min_length=3, max_length=255)
    marca_modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    fecha_registro: Optional[datetime] = Field(default=None)
    persona_id: Optional[int] = Field(default=None)

class EquipoEstado(BaseModel):
    estado: Optional[bool] = None

class EquipoOut(EquipoBase):
    id_equipo: int
    nombre_completo: str
    persona_id: int

class PaginatedEquipos(BaseModel):
    page: int
    page_size: int
    total_equipements: int
    total_pages: int
    equipos: List[EquipoOut]
    