from pydantic import BaseModel, Field
from typing import Optional

class RolesBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    descripcion: str = Field(min_length=3, max_length=255)
    estado: bool

class RolesCreate(RolesBase):
    pass

class RolesUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=50)
    descripcion: Optional[str] = Field(default=None, min_length=3, max_length=255)
    
class RolesEstado(BaseModel):
    estado: Optional[bool] = None

class RolesOut(RolesBase):
    id_rol: int
