from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MovementBase(BaseModel):
    autorizacion_id: Optional[int] = None
    tipo_id: int
    usuario_registra: int
    fecha_movimiento: datetime

class MovementCreate(MovementBase):
    pass

class MovementUpdate(BaseModel):
    tipo_id: Optional[int] = None

class MovementOut(MovementBase):
    id_movimiento_sede: int 
    serial_equipo:str
    categoria_id:int
    nombre_categoria:str
    nombre_usuario: str
    nombre_tipo: str

class PaginatedMovements(BaseModel):
    page: int
    page_size: int
    total_movements: int
    total_pages: int
    movements: List[MovementOut]
    
