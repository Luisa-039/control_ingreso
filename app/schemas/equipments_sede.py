from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class TipoEquipo_sede(str, Enum):
    portatil = "Portátil"
    pc = "PC Mesa"
    herramienta = "Herramienta"
    otro = "Otro"

class Estado_equip_sede(str, Enum):
    disponible = "Disponible"
    mantenimiento = "Mantenimiento"
    fuera_de_sede = "Fuera_de_sede"
    inactivo = "Inactivo"
    
class Equipo_sedeBase(BaseModel):
    sede_id: int
    categoria: Optional[TipoEquipo_sede] = None
    serial: Optional[str] = None
    descripcion: Optional[str] = None
    marca_modelo: str
    fecha_registro: datetime
    estado: Estado_equip_sede
    codigo_barras_equipo: Optional[str] = None

class Equipo_sedeCreate(Equipo_sedeBase):
    pass

class Equipo_sedeUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    categoria: Optional[TipoEquipo_sede] = None
    marca_modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    fecha_registro: Optional[datetime] = Field(default=None)
    sede_id: Optional[int] = Field(default=None)

class Equipo_sedeEstado(BaseModel):
    estado: Estado_equip_sede

class Equipo_sedeOut(Equipo_sedeBase):
    id_equipo_sede: int
    sede_id: int
    nombre: str
   
    
class PaginatedEquipos_sede(BaseModel):
    page: int
    page_size: int
    total_equipements: int
    total_pages: int
    equipos: List[Equipo_sedeOut]
