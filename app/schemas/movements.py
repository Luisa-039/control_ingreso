from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class TipoMovimiento (str, Enum):
    entrada = "Entrada"
    salida = "Salida"
    traslado = "Traslado"

class MovementBase(BaseModel):
    equipo_id: int
    autorizacion_id: int
    tipo_movimiento: TipoMovimiento
    usuario_registra: int
    fecha_movimiento: datetime

class MovementCreate(MovementBase):
    pass

class MovementUpdate(BaseModel):
    tipo_movimiento: Optional[TipoMovimiento] = None

class MovementOut(MovementBase):
    id_movimiento_sede: int
