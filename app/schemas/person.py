from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class TipoPersona (str, Enum):
    sena = "Sena"
    visitante = "Visitante"

class TipoDocumento (str, Enum):
    cc = "CC"
    ti = "TI"
    ce = "CE"
    pasaporte = "pasaporte"

class PersonBase(BaseModel):
    tipo_persona: TipoPersona
    tipo_documento: TipoDocumento
    documento: str = Field(min_length=8, max_length=20)
    nombre_completo: str = Field(min_length=3, max_length=50)
    codigo_barras: Optional[str] = Field(default=None, min_length=3, max_length=100)    
    fecha_registro: datetime
    estado: bool

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    tipo_persona: Optional[TipoPersona]
    tipo_documento: Optional[TipoDocumento]
    documento: Optional[str] = Field(default=None, min_length=8, max_length=20)
    nombre_completo: Optional[str] = Field(default=None, min_length=3, max_length=50)
    
class PersonEstado(BaseModel):
    estado: Optional[bool] = None

class PersonOut(PersonBase):
    id_persona: int