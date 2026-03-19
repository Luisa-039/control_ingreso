from pydantic import BaseModel, Field
from typing import List, Optional

class EncuestaBase(BaseModel): 
    acceso_id: int = Field(gt=0)
    calificacion: int = Field(ge=1, le=5)
    observacion: str = Field(min_length=1, max_length=255)

    
class EncuestaCreate(EncuestaBase):
    pass

class EncuestaUpdate(BaseModel):
    calificacion: Optional[int] = Field(None, ge=1, le=5)
    observacion: Optional[str] = Field(None, min_length=1, max_length=255)

class EncuestaState(BaseModel):
    estado_encuesta: bool

class EncuestaOut(EncuestaBase):
    id_encuesta: int
    nombre_completo: str
    estado_encuesta: bool
    nombre_area: Optional[str] = None
    nombre_sede: Optional[str] = None

class PaginatedEncuesta(BaseModel):
    page: int
    page_size: int
    total_encuesta: int
    total_pages: int
    encuestas: List[EncuestaOut]