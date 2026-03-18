from pydantic import BaseModel, Field
from typing import Optional

#Creación de esquemas para la creación de tipos de movimientos
class TypeBase(BaseModel):
    nombre_tipo: str = Field(min_length=3, max_length=50)
    descripcion: str = Field(min_length=3, max_length=255)

class TypeCreate(TypeBase):
    pass

class TypeUpdate(BaseModel):
    nombre_tipo: Optional[str] = Field(default=None, min_length=3, max_length=50)
    descripcion: Optional[str] = Field(default=None, min_length=3, max_length=255)

class TypeOut(TypeBase):
    id_tipo: int
