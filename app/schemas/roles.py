
from pydantic import BaseModel, Field


class RolesBase(BaseModel):
    nombre: str
    descripcion: str

class RolesOut(RolesBase):
    id_rol: int
