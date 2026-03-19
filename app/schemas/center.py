from pydantic import BaseModel, Field
from typing import Optional

class CenterBase(BaseModel):
    codigo_centro: str = Field(min_length=1, max_length=15)
    nombre: str = Field(min_length=3, max_length=100)
    ciudad_id: int

class CenterCreate(CenterBase):
    pass

class CenterUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=100)
    ciudad_id: Optional[int] = None
   
class CenterEstado(BaseModel):
    estado:bool

class CenterOut(CenterBase):
    id_centro: int
    estado: bool
    nombre_ciudad:str
