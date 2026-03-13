from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TipoMovimiento (str, Enum):
    entrada = "Entrada"
    salida = "Salida"
    traslado = "Traslado"

class MovementBase(BaseModel):
    equipo_id: int
    autorizacion_id: Optional[int] = None
    tipo_movimiento: TipoMovimiento
    usuario_registra: int
    fecha_movimiento: datetime

class MovementCreate(MovementBase):
    pass

class MovementUpdate(BaseModel):
    tipo_movimiento: TipoMovimiento

class MovementOut(MovementBase):
    id_movimiento_sede: int 
    serial_equipo:str
    categoria:str
    nombre_usuario: str
    
class PaginatedMovements(BaseModel):
    page: int
    page_size: int
    total_movements: int
    total_pages: int
    movements: List[MovementOut]
    
