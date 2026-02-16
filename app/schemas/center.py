from pydantic import BaseModel, Field
from typing import Optional

class CenterBase(BaseModel):
    codigo_centro: str = Field(min_length=3, max_length=15)
    nombre: str = Field(min_length=3, max_length=100)
    estado: bool

class CenterCreate(CenterBase):
    pass

class CenterUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=100)

class CenterEstado(BaseModel):
    estado: Optional[bool] = None

class CenterOut(CenterBase):
    id_centro: int