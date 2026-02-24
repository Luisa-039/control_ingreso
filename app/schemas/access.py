from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AccessBase(BaseModel): 
    sede_id: int 
    persona_id: int 
    equipo_id: Optional[int] = None  
    usuario_registro_id: int 
    documento: str 
    tipo_movimiento: bool 
    fecha_entrada: datetime 

class AccessCreate(AccessBase):
    pass

class AccesUpdate(AccessBase):
    sede_id: Optional[int] = None 
    persona_id: Optional[int] = None 
    equipo_id: Optional[int] = None 
    usuario_registro_id: Optional[int] = None 
    documento: Optional[str] = None 
    tipo_movimiento: Optional[bool] 
    fecha_entrada: Optional[datetime] = None 
    fecha_salida: Optional[datetime] = None
    
class AccessOut(AccessBase):
    id_acceso: int
    fecha_salida: Optional[datetime] = None
