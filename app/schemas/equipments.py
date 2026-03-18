from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

# Definición de modelos Pydantic para equipos
class EquipoBase(BaseModel):
    serial: Optional[str] = None
    descripcion: str
    categoria_id: int
    foto_path: Optional[str]
    marca_modelo: str
    persona_id: int
    fecha_registro: datetime
    estado: bool
    codigo_barras_inv: Optional[str] = None

class EquipoCreate(EquipoBase):
    pass

#Requisitos para actualizar un equipo, todos los campos son opcionales
class EquipoUpdate(BaseModel):
    serial: Optional[str] = Field(default=None,min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    categoria_id: Optional[int] = None
    foto_path: Optional[str] = Field(default=None, min_length=3, max_length=255)
    marca_modelo: Optional[str] = Field(default=None,min_length=3, max_length=255)
    fecha_registro: Optional[datetime] = Field(default=None)
    persona_id: Optional[int] = Field(default=None)

# Solo se puede actualizar el estado del equipo
class EquipoEstado(BaseModel):
    estado: Optional[bool] = None

# Modelo de salida para un equipo, incluye el ID y el nombre completo de la persona asociada
class EquipoOut(EquipoBase):
    id_equipo: int
    nombre_completo: str
    persona_id: int

# Modelo para la paginación de equipos, incluye información sobre la página actual, el tamaño de página, el total de equipos, 
# el total de páginas y la lista de equipos en la página actual
class PaginatedEquipos(BaseModel):
    page: int
    page_size: int
    total_equipements: int
    total_pages: int
    equipos: List[EquipoOut]