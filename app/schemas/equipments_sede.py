from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class Estado_equip_sede(str, Enum):
    disponible = "Disponible"
    mantenimiento = "Mantenimiento"
    fuera_de_sede = "Fuera_de_sede"
    inactivo = "Inactivo"

#Este es para crear el modelo base 
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

#Modelo para el modelo de los equipos
class Equipo_sedeCreate(Equipo_sedeBase):
    pass

#Modelo para actualizar información de los equipo
class Equipo_sedeUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    categoria_id: Optional[int] = Field(default=None)
    area_id: Optional[int] = Field(default=None)
    marca: Optional[str] = Field(default=None,min_length=3, max_length=255)
    modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    sede_id: Optional[int] = Field(default=None)

#Modelo para manejar los estados
class Equipo_sedeEstado(BaseModel):
    estado: Estado_equip_sede

#Modelo de salida 
class Equipo_sedeOut(Equipo_sedeBase):
    id_equipo_sede: int
    sede_id: int
    nombre_sede: str
    nombre_categoria: str
    nombre_area: str
   
#Modelo para la paginación  
class PaginatedEquipos_sede(BaseModel):
    page: int
    page_size: int
    total_equipements: int
    total_pages: int
    equipos: List[Equipo_sedeOut]
