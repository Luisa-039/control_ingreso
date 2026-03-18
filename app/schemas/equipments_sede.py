from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class Estado_equip_sede(str, Enum):
    disponible = "Disponible"
    mantenimiento = "Mantenimiento"
    fuera_de_sede = "Fuera_de_sede"
    inactivo = "Inactivo"
    
class Equipo_sedeBase(BaseModel):
    sede_id: int
    categoria_id: int
    serial: Optional[str] = None
    descripcion: Optional[str] = None
    marca: str
    modelo: str
    area_id:int
    fecha_registro: datetime
    estado: Estado_equip_sede
    codigo_barras_equipo: Optional[str] = None

class Equipo_sedeCreate(Equipo_sedeBase):
    pass

class Equipo_sedeUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    categoria_id: Optional[int] = Field(default=None)
    area_id: Optional[int] = Field(default=None)
    marca: Optional[str] = Field(default=None,min_length=3, max_length=255)
    modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    fecha_registro: Optional[datetime] = Field(default=None)
    sede_id: Optional[int] = Field(default=None)

class Equipo_sedeEstado(BaseModel):
    estado: Estado_equip_sede

class Equipo_sedeOut(Equipo_sedeBase):
    id_equipo_sede: int
    sede_id: int
    nombre_sede: str
   
    
class PaginatedEquipos_sede(BaseModel):
    page: int
    page_size: int
    total_equipements: int
    total_pages: int
    equipos: List[Equipo_sedeOut]
