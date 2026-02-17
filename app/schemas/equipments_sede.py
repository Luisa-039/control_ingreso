from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TipoEquipo_sede(str, Enum):
    portatil = "Portátil"
    pc = "PC Mesa"
    herramienta = "Herramienta"
    otro = "Otro"

class Estado_equip_sede(str, Enum):
    disponible = "Disponible",
    mantenimiento = "Mantenimiento",
    fuera_de_sede = "Fuera de sede"
    inactivo = "Inactivo"
    
class Equipo_sedeBase(BaseModel):
    sede_id: int
    categoria: Optional[TipoEquipo_sede] = None
    serial: Optional[str] = None
    descripcion: Optional[str] = None
    marca_modelo: str
    fecha_registro: datetime
    estado: Estado_equip_sede

class Equipo_sedeCreate(Equipo_sedeBase):
    codigo_barras_equipo: Optional[str] = None

class Equipo_sedeUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    categoria: Optional[TipoEquipo_sede] = None
    marca_modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    fecha_registro: Optional[datetime] = Field(default=None)
    sede_id: Optional[int] = Field(default=None)

class Equipo_sedeEstado(BaseModel):
    estado: Optional[Estado_equip_sede] = None

class Equipo_sedeOut(BaseModel):
    id_equipo_sede: int
    sede_id: int
    categoria: Optional[TipoEquipo_sede] = None
    codigo_barras_equipo: Optional[str] = None
    serial: Optional[str] = None
    descripcion: Optional[str] = None
    marca_modelo: str
    fecha_registro: datetime
    estado: Estado_equip_sede
