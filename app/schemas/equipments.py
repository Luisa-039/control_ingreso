from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TipoEquipo(str, Enum):
    computador = "Computador"
    herramienta = "Herramienta"
    otro = "Otro"
    
class EquipoBase(BaseModel):
    serial: Optional[str] = None
    descripcion: str
    tipo_equipo: Optional[TipoEquipo] = None
    foto_path: str
    marca_modelo: str
    persona_id: int
    fecha_registro: datetime
    estado: bool

class EquipoCreate(EquipoBase):
    codigo_barras_inv: Optional[str] = None

class EquipoUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    tipo_equipo: Optional[TipoEquipo] = None
    foto_path: Optional[str] = Field(default=None, min_length=3, max_length=255)
    marca_modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    fecha_registro: Optional[datetime] = Field(default=None)
    persona_id: Optional[int] = Field(default=None)
    estado: Optional[bool] = Field(default=None)

class EquipoEstado(BaseModel):
    estado: Optional[bool] = None

class EquipoOut(BaseModel):
    id_equipo: int
    serial: Optional[str] = None
    codigo_barras_inv: Optional[str] = None
    descripcion: str
    tipo_equipo: TipoEquipo
    foto_path: str
    marca_modelo: str
    persona_id: int
    fecha_registro: datetime

