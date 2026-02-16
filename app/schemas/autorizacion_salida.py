from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AutorizacionSalidaBase(BaseModel):
    equipo_id: int
    usuario_id_autoriza: int
    fecha_autorizacion: datetime
    destino: str = Field(min_length=3, max_length=50)
    motivo: str = Field(min_length=3, max_length=255)
    estado: bool


class AutorizacionSalidaCreate(AutorizacionSalidaBase):
    pass

class AutorizacionSalidaUpdate(BaseModel):
    id_salida: Optional[int] = None
    equipo_id: Optional[int] = None
    usuario_id_autoriza: Optional[int] = None
    fecha_autorizacion: Optional[datetime] = Field(default=None)
    destino: Optional[str] = Field(default=None, min_length=3, max_length=100)
    motivo: Optional[str] = Field(default=None, min_length=3, max_length=255)

class AutorizacionEstado(BaseModel):
    estado: Optional[bool] = None

class AutorizacionSalidaOut(AutorizacionSalidaBase):
    id_autorizacion: int
    usuario_id_autoriza: int