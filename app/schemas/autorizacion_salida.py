from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class AutorizacionSalidaBase(BaseModel):
    equipo_id: int
    usuario_id_autoriza: int
    fecha_autorizacion: datetime
    tipo_id: int
    destino: str = Field(min_length=3, max_length=50)
    motivo: str = Field(min_length=3, max_length=255)
    estado: bool = Field(default=False)


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
    estado: bool
    fecha_movimiento: datetime 

class AutorizacionSalidaOut(AutorizacionSalidaBase):
    id_autorizacion: int
    nombre_usuario: str
    serial: str
    nombre_tipo: str
    nombre_categoria: str
    
class PaginatedAuth_salida(BaseModel):
    page: int
    page_size: int
    total_auth_salida: int
    total_pages: int
    auth_salida: List[AutorizacionSalidaOut]
    
